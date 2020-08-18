==========================
plone.recipe.zope2instance
==========================


This is the doctest for plone.recipe.zope2instance. It ensures the template
works fine. It is based on zc.buildout testing module::

    >>> from __future__ import print_function
    >>> from zc.buildout.testing import *
    >>> from os.path import join
    >>> import sys, os
    >>> options = globals()
    >>> WINDOWS = sys.platform == 'win32'


DemoStorage
===========

To have a DemoStorage configuration, you can use demo-storage::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... eggs =
    ... user = me:me
    ... file-storage = newfs/Data.fs
    ... demo-storage = on
    ...
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

We should have a zope instance, with a basic zope.conf::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    ...
    <zodb_db main>
        # Main database
        cache-size 30000
    <BLANKLINE>
    # DemoStorage
        <demostorage>
    <BLANKLINE>
        # FileStorage database
        <filestorage>
          path .../sample-buildout/var/newfs/Data.fs
        </filestorage>
    <BLANKLINE>
        </demostorage>
        mount-point /
    </zodb_db>
    ...
    <BLANKLINE>

Verify that demostorage can be disable::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... eggs =
    ... user = me:me
    ... file-storage = newfs/Data.fs
    ... demo-storage = off
    ...
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

We should have a zope instance, with a basic zope.conf without demostorage::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    ...
    <zodb_db main>
        # Main database
        cache-size 30000
    <BLANKLINE>
    # Blob-enabled FileStorage database
        <blobstorage>
          blob-dir .../sample-buildout/var/blobstorage
          # FileStorage database
          <filestorage>
            path .../sample-buildout/var/newfs/Data.fs
          </filestorage>
        </blobstorage>
        mount-point /
    </zodb_db>
    ...
    <BLANKLINE>

You can add file storage to the demo-storage to be able to keep
changes::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... eggs =
    ... user = me:me
    ... file-storage = newfs/Data.fs
    ... demo-storage = on
    ... demo-file-storage = demofs/Data.fs
    ...
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

We should have a zope instance, with a basic zope.conf::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    ...
    <zodb_db main>
        # Main database
        cache-size 30000
    <BLANKLINE>
    # DemoStorage
        <demostorage>
    <BLANKLINE>
        # FileStorage database
        <filestorage base>
          path .../sample-buildout/var/newfs/Data.fs
        </filestorage>
    <BLANKLINE>
    <BLANKLINE>
        # FileStorage database
        <filestorage changes>
          path .../sample-buildout/var/demofs/Data.fs
        </filestorage>
    <BLANKLINE>
        </demostorage>
        mount-point /
    </zodb_db>
    ...
    <BLANKLINE>

You can add a blob storage to the demo-storage as well::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... eggs =
    ... user = me:me
    ... file-storage = newfs/Data.fs
    ... blob-storage = ${buildout:directory}/var/blob
    ... demo-storage = on
    ... demo-file-storage = demofs/Data.fs
    ... demo-blob-storage = ${buildout:directory}/var/demoblob
    ...
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

We should have a zope instance, with a basic zope.conf::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    ...
        <blobstorage base>
          blob-dir .../sample-buildout/var/blob
          # FileStorage database
          <filestorage>
            path .../sample-buildout/var/newfs/Data.fs
          </filestorage>
        </blobstorage>
    ...
        <blobstorage changes>
          blob-dir .../sample-buildout/var/demoblob
          # FileStorage database
          <filestorage>
            path .../sample-buildout/var/demofs/Data.fs
          </filestorage>
        </blobstorage>
    ...

Finally, you can add only a blob storage. Changes will then not be
persisted on disk, but blob support will be available separately (it's
not supported by the in-memory demostorage)::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... eggs =
    ... user = me:me
    ... file-storage = newfs/Data.fs
    ... demo-storage = on
    ... demo-blob-storage = ${buildout:directory}/var/demoblob
    ...
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

We should have a zope instance, with a basic zope.conf::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    ...
    <zodb_db main>
        # Main database
        cache-size 30000
    <BLANKLINE>
    # DemoStorage
        <demostorage>
    <BLANKLINE>
        # FileStorage database
        <filestorage base>
          path .../sample-buildout/var/newfs/Data.fs
        </filestorage>
    <BLANKLINE>
    <BLANKLINE>
        # Blob-enabled FileStorage database
        <blobstorage changes>
          blob-dir .../sample-buildout/var/demoblob
          <demostorage />
        </blobstorage>
    <BLANKLINE>
        </demostorage>
        mount-point /
    </zodb_db>
    ...

