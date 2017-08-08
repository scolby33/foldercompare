foldercompare
=============
Compare folder contents via hash.

.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :alt: Python 3.6
    
Installation
------------
At the moment, installation must be performed via GitHub:

.. code-block:: sh

    $ pip install git+git://github.com/scolby33/foldercompare.git
    
:code:`foldercompare` supports only Python 3.6.

Demo
----

.. code-block:: console

    $ mkdir -p /tmp/demo/a /tmp/demo/b  # just some setup
    $ cd /tmp/demo
    $ touch a/a a/b a/c b/a b/b b/d
    $ echo "DIFFERENT CONTENT" >> a/b
    
    $ foldercompare a b  # the simplest case--compare two folders
    9fb5d41e2533b73381bdde8e3ac2d60a6a18467674771187595d83e9bfa30909 /tmp/demo/a/b
    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/b/b

    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/a/c
    ABSENT /tmp/demo/b/c

    ABSENT /tmp/demo/a/d
    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/b/d

    $ # you can change the hash algorithm!
    $ # all of the algorithms in your Python's `hashlib` are available
    $ # default is sha3_256
    $ foldercompare -s md5 a b  
    128edd12d0b04e23d10c4747d0da2c03 /tmp/demo/a/b
    d41d8cd98f00b204e9800998ecf8427e /tmp/demo/b/b

    d41d8cd98f00b204e9800998ecf8427e /tmp/demo/a/c
    ABSENT /tmp/demo/b/c

    ABSENT /tmp/demo/a/d
    d41d8cd98f00b204e9800998ecf8427e /tmp/demo/b/d

    $ # it works with relative paths, too
    $ cd a
    $ foldercompare . ../b
    9fb5d41e2533b73381bdde8e3ac2d60a6a18467674771187595d83e9bfa30909 /tmp/demo/a/b
    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/b/b

    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/a/c
    ABSENT /tmp/demo/b/c

    ABSENT /tmp/demo/a/d
    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/b/d

    $ # you can do the hashing separately and compare at a later time
    $ cd ..
    $ foldercompare a > a.txt
    $ foldercompare b > b.txt
    $ foldercompare -a a.txt -b b.txt
    9fb5d41e2533b73381bdde8e3ac2d60a6a18467674771187595d83e9bfa30909 /tmp/demo/a/b
    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/b/b

    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/a/c
    ABSENT /tmp/demo/b/c

    ABSENT /tmp/demo/a/d
    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/b/d

    $ # the format of the hash files is simple: {hash_value}<SP>{full_path}
    $ cat a.txt
    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/a/a
    9fb5d41e2533b73381bdde8e3ac2d60a6a18467674771187595d83e9bfa30909 /tmp/demo/a/b
    a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a /tmp/demo/a/c

Contributing
------------
There are many ways to contribute to an open-source project, but the two most common are reporting bugs and contributing code.

If you have a bug or issue to report, please visit the `issues page on Github <https://github.com/scolby33/foldercompare/issues>`_ and open an issue there.

License
-------

MIT. See the :code:`LICENSE.rst` file for more information.
