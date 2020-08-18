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


ZEO storage
===========

If you want to connect to a zeo server you specify some additional properties
for the plone.recipe.zope2instance recipe.

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
    ... zeo-client = yes
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
        ...
        <zeoclient>
            read-only false
            read-only-fallback false
            blob-dir .../sample-buildout/var/blobcache
            shared-blob-dir no
            server 8100
            storage 1
            name zeostorage
            cache-size 128MB
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
        </zeoclient>
        ...
    </zodb_db>
    ...
    <BLANKLINE>

If `zeo-client-client` and other relevant ZEO options such as
`zeo-client-blob-cache-size` and `zeo-client-blob-cache-size-check` are
specified, they should get included in that section as well.

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
    ... zeo-client = yes
    ... zeo-client-client = persistentcache88
    ... min-disconnect-poll = 10
    ... max-disconnect-poll = 20
    ... zeo-client-blob-cache-size = 5GB
    ... zeo-client-blob-cache-size-check = 50
    ... zeo-client-read-only-fallback = true
    ... zeo-var = %(sample_buildout)s/var
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
        ...
        <zeoclient>
            read-only false
            read-only-fallback true
            blob-dir .../sample-buildout/var/blobcache
            shared-blob-dir no
            server 8100
            storage 1
            name zeostorage
            cache-size 128MB
            blob-cache-size 5GB
            blob-cache-size-check 50
    <BLANKLINE>
            var .../sample-buildout/var
            client persistentcache88
            min-disconnect-poll 10
            max-disconnect-poll 20
        </zeoclient>
        ...
    </zodb_db>
    ...
    <BLANKLINE>

Verify that demo-storage is correctly applied

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
    ... zeo-client = yes
    ... demo-storage = yes
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
        ...
        # DemoStorage
        <demostorage>
        # ZEOStorage database
        <zeoclient>
            read-only false
            read-only-fallback false
            server 8100
            storage 1
            name zeostorage
            cache-size 128MB
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
        </zeoclient>
        </demostorage>
        ...
    </zodb_db>
    ...
    <BLANKLINE>

Verify that blob-storage is correctly applied

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
    ... zeo-client = yes
    ... blob-storage = ${buildout:directory}/var/blob
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
        ...
    # Blob-enabled ZEOStorage database
        <zeoclient>
          read-only false
          read-only-fallback false
          blob-dir .../sample-buildout/var/blob
          shared-blob-dir no
          server 8100
          storage 1
          name zeostorage
          cache-size 128MB
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
        </zeoclient>
        ...
    </zodb_db>
    ...
    <BLANKLINE>

Verify that demo-storage is correctly applied together with
before-storage::

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
    ... zeo-client = yes
    ... demo-storage = yes
    ... before-storage = now
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
        # Blob-enabled ZEOStorage database
          <zeoclient>
            read-only false
            read-only-fallback false
            blob-dir .../sample-buildout/var/blobcache
            shared-blob-dir no
            server 8100
            storage 1
            name zeostorage
            cache-size 128MB
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
          </zeoclient>
        </before>
    <BLANKLINE>
        </demostorage>
        mount-point /
    </zodb_db>
    ...
    <BLANKLINE>

You can get specific zeo server address using `zeo-address`.

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
    ... zeo-client = yes
    ... zeo-address = 127.0.0.1:8101
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
        ...
        <zeoclient>
            read-only false
            read-only-fallback false
            blob-dir .../sample-buildout/var/blobcache
            shared-blob-dir no
            server 127.0.0.1:8101
            storage 1
            name zeostorage
            cache-size 128MB
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
        </zeoclient>
        ...
    </zodb_db>
    ...
    <BLANKLINE>

You can also set multiple zeo server addresses using `zeo-address`.

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
    ... zeo-client = yes
    ... zeo-address = 127.0.0.1:8101 127.0.0.1:8102
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
        ...
        <zeoclient>
            read-only false
            read-only-fallback false
            blob-dir .../sample-buildout/var/blobcache
            shared-blob-dir no
            server 127.0.0.1:8101
            server 127.0.0.1:8102
            storage 1
            name zeostorage
            cache-size 128MB
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
        </zeoclient>
        ...
    </zodb_db>
    ...
    <BLANKLINE>

