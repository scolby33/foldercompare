#!/usr/bin/env python3
"""Compare folder contents via hash.
File I/O and hashing are done in threads to take advantage of possible speedups.
Call with two directory names to hash the contents of each and print information about their differences.
Call with one directory name to output hashes of each file within.
Call with `-a` and `-b` to input files containing output as from above to compare.

Usage:
    foldercompare [-v] [-s <hash_spec>] [-j <num_workers>] <dir_a> [<dir_b>]
    foldercompare -a <a_file> -b <b_file>

Options:
    -v                  Verbose output
    -s <hash_spec>      Set the hashing algorithm. Use a name from `hashlib`, e.g. 'md5'. [default: sha3_256]
    -j <num_workers>    The number asynchronous hashing workers to spawn. Defaults to the number of CPU's + 1
    -a <a_file>         The first file of hashes to compare
    -b <b_file>         The second file of hashes to compare
"""
import hashlib
import logging
import multiprocessing
import os
import sys
import time

import curio
from docopt import docopt

BLOCKSIZE = 2**16
logger = logging.getLogger(__name__)


def walk_all_files(path):
    for dirpath, _, filenames in os.walk(os.path.expanduser(path)):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


async def hash_file_worker(work_queue, output, output_lock, hash_func):
    while True:
        dir_id, path = await work_queue.get()
        digest = await curio.workers.run_in_thread(hash_file, path, hash_func)
        async with output_lock:
            output[dir_id][path] = digest
        await work_queue.task_done()


def hash_file(path, hash_func):
    start = time.time()
    hasher = hash_func()
    # async with curio.file.aopen(path, 'rb') as f:
    #     buf = await f.read(BLOCKSIZE)
    #     while len(buf) > 0:
    #         hasher.update(buf)
    #         buf = await f.read(BLOCKSIZE)
    with open(path, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)

    digest = hasher.hexdigest()
    end = time.time()
    logger.debug(f'{end - start:.9f}s {path}')
    return digest


def normalize_paths(input):
    prefix = os.path.commonpath(input.keys())
    prefix_len = len(prefix) + 1
    normalized = {k[prefix_len:]: v for k, v in input.items()}
    return prefix, normalized


def compare_hashes(a, b):
    combined = {}
    for key in (a.keys() | b.keys()):
        combined[key] = (a.get(key, None), b.get(key, None))
    bad = (k for k, v in combined.items()
           if v[0] != v[1] and v[0] is not None and v[1] is not None)
    a_missing = (k for k, v in combined.items() if v[0] is None)
    b_missing = (k for k, v in combined.items() if v[1] is None)

    return bad, a_missing, b_missing


async def amain(hash_func, a, b=None, num_workers=None):
    work_queue = curio.Queue()
    output_lock = curio.Lock()

    output = {'a': {}}
    if b:
        output['b'] = {}

    hashers = curio.TaskGroup(name='hashers')
    if not num_workers:
        try:
            num_workers = multiprocessing.cpu_count() + 1
        except NotImplementedError:
            num_workers = 2
    for _ in range(num_workers):
        await hashers.spawn(hash_file_worker, work_queue, output, output_lock,
                            hash_func)

    for fullpath in walk_all_files(a):
        await work_queue.put(('a', fullpath))
    if b:
        for fullpath in walk_all_files(b):
            await work_queue.put(('b', fullpath))

    await work_queue.join()
    await hashers.cancel_remaining()

    return output


def main():
    args = docopt(__doc__)
    log_format = '%(levelname)s: %(message)s'
    if args['-v']:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    if not args['-a'] and not args['-b']:  # we're being asked to hash some files
        if (not os.path.isdir(args['<dir_a>'])) or (
                args['<dir_b>'] and not os.path.isdir(args['<dir_b>'])
        ):  # use short-circuit of the and to only call os.isdir if "dir_b" was actually provided
            logger.error(
                'Must provide two directories to hash. Were you looking for the `-a` and `-b` options?'
            )
            return 1
        try:
            hash_func = getattr(hashlib, args['-s'])
        except AttributeError:
            hash_func = hashlib.sha3_256
            logger.warn(
                f'Hash function {args["-s"]} is not available. Defaulting to sha3_256'
            )

        output = curio.run(amain, hash_func, args['<dir_a>'], args['<dir_b>'],
                           int(args['-j']) if args['-j'] else None)

        if not args['<dir_b>']:  # only one input folder, so just print the hashes and exit
            for k, v in sorted(output['a'].items()):
                print(f'{v} {k}')
            return
    else:  # we're given some file hashes already so just compare them
        output = {}
        with open(args['-a'], 'r') as f:
            output['a'] = dict(
                reversed(line.strip().split(None, 1)) for line in f)
        with open(args['-b'], 'r') as f:
            output['b'] = dict(
                reversed(line.strip().split(None, 1)) for line in f)

    a_prefix, a_normalized = normalize_paths(output['a'])
    b_prefix, b_normalized = normalize_paths(output['b'])
    bad, a_missing, b_missing = compare_hashes(a_normalized, b_normalized)

    dirty = False  # this feels hacky, but I can't think of a better way...
    for path in sorted(bad):
        dirty = True
        print(f'{a_normalized[path]} {os.path.join(a_prefix, path)}')
        print(f'{b_normalized[path]} {os.path.join(b_prefix, path)}')
        print()
    for path in sorted(b_missing):
        dirty = True
        print(f'{a_normalized[path]} {os.path.join(a_prefix, path)}')
        print(f'ABSENT {os.path.join(b_prefix, path)}')
        print()
    for path in sorted(a_missing):
        dirty = True
        print(f'ABSENT {os.path.join(a_prefix, path)}')
        print(f'{b_normalized[path]} {os.path.join(b_prefix, path)}')
        print()

    if dirty:  # We had something to report--missing files or bad hashes--so give a bad return status to the caller.
        return 1


if __name__ == '__main__':
    sys.exit(main())
