================================================
plone.recipe.zope2instance TEMPORARY STORAGE OFF
================================================


This is the doctest for plone.recipe.zope2instance. It ensures the template
works fine. It is based on zc.buildout testing module::

    >>> from __future__ import print_function
    >>> from zc.buildout.testing import *
    >>> from os.path import join
    >>> import sys, os
    >>> options = globals()
    >>> WINDOWS = sys.platform == 'win32'


Turning off ZODB temporary storage
==================================
Zope 4 does not ship with the required packages anymore, so to avoid breakage
the creation of the ZODB temporary storage definition can be turned off:

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
    ... zodb-temporary-storage = off
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

The generated configuration has no temporary storage section anymore:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    instancehome $INSTANCEHOME
    %define CLIENTHOME .../sample-buildout/var/instance
    clienthome $CLIENTHOME
    debug-mode off
    security-policy-implementation C
    verbose-security off
    default-zpublisher-encoding utf-8
    <environment>
        CHAMELEON_CACHE .../var/cache
    </environment>
    <zodb_db main>
        # Main database
        cache-size 30000
        # Blob-enabled FileStorage database
        <blobstorage>
          blob-dir .../sample-buildout/var/blobstorage
          # FileStorage database
          <filestorage>
            path .../sample-buildout/var/filestorage/Data.fs
          </filestorage>
        </blobstorage>
        mount-point /
    </zodb_db>
    python-check-interval 1000

Leaving the option empty should have the same result,
as this was previously the way to disable it::

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
    ... zodb-temporary-storage =
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

The generated configuration should be the same as from the previous run.

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf2 = fd.read()
    >>> zope_conf2 = zope_conf2.replace('\\', '/')
    >>> zope_conf == zope_conf2
    True


Explicit ZODB temporary storage
===============================

You can also explicitly set an own ZODB temporary storage definition:

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
    ... zodb-temporary-storage = <some config />
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

The generated configuration has our explicit temporary storage section:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    instancehome $INSTANCEHOME
    %define CLIENTHOME .../sample-buildout/var/instance
    clienthome $CLIENTHOME
    debug-mode off
    security-policy-implementation C
    verbose-security off
    default-zpublisher-encoding utf-8
    <environment>
        CHAMELEON_CACHE .../var/cache
    </environment>
    <zodb_db main>
        # Main database
        cache-size 30000
        # Blob-enabled FileStorage database
        <blobstorage>
          blob-dir .../sample-buildout/var/blobstorage
          # FileStorage database
          <filestorage>
            path .../sample-buildout/var/filestorage/Data.fs
          </filestorage>
        </blobstorage>
        mount-point /
    </zodb_db>
    <some config />
    python-check-interval 1000

