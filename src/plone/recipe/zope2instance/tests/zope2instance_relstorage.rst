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


RelStorage
==========

To have a RelStorage configuration, you can use rel-storage::

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
    ... rel-storage =
    ...   type postgresql
    ...   dbname zodb
    ...   user tarek
    ...   host example.com
    ...   password secret space
    ...   keep-history false
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
    %import relstorage
        <relstorage>
            keep-history false
            <postgresql>
                dsn dbname='zodb' user='tarek' host='example.com' password='secret space'
            </postgresql>
        </relstorage>
        mount-point /
    </zodb_db>
    ...
    <BLANKLINE>

Relstorage and sqlite3::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... wsgi = off
    ... eggs =
    ... user = me:me
    ... rel-storage =
    ...   type sqlite3
    ...   data-dir %(sample_buildout)s/var/db
    ...   pragmas-synchronous off
    ...   pragmas-checkpoint_fullfsync off
    ... ''' % options)

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

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
        %import relstorage
        <relstorage>
            <sqlite3>
                data-dir .../sample-buildout/var/db
                <pragmas>
                    checkpoint_fullfsync off
                    synchronous off
                </pragmas>
            </sqlite3>
        </relstorage>
        mount-point /
    </zodb_db>
    ...
    <BLANKLINE>
