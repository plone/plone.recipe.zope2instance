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


BeforeStorage
=============

To have a BeforeStorage configuration, you can use before-storage::

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
    ... before-storage = now
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
    %import zc.beforestorage
        # BeforeStorage
        <before>
          before now
    <BLANKLINE>
          # Blob-enabled FileStorage database
          <blobstorage>
            blob-dir .../sample-buildout/var/blobstorage
            # FileStorage database
            <filestorage>
              path .../sample-buildout/var/newfs/Data.fs
            </filestorage>
          </blobstorage>
    <BLANKLINE>
        </before>
        mount-point /
    </zodb_db>
    ...
    <BLANKLINE>

The before-storage option can be combined with a demo-storage::

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
    ... before-storage = now
    ... demo-storage = on
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
        %import zc.beforestorage
        # BeforeStorage
        <before>
          before now
    <BLANKLINE>
          # Blob-enabled FileStorage database
          <blobstorage>
            blob-dir .../sample-buildout/var/blobstorage
            # FileStorage database
            <filestorage>
              path .../sample-buildout/var/newfs/Data.fs
            </filestorage>
          </blobstorage>
    <BLANKLINE>
        </before>
    <BLANKLINE>
    <BLANKLINE>
        </demostorage>
        mount-point /
    </zodb_db>
    ...
    <BLANKLINE>
