======================================
plone.recipe.zope2instance BASIC USAGE
======================================


This is the doctest for plone.recipe.zope2instance. It ensures the template
works fine. It is based on zc.buildout testing module::

    >>> from __future__ import print_function
    >>> from zc.buildout.testing import ls, write
    >>> from os.path import join
    >>> import sys, os
    >>> options = globals()
    >>> WINDOWS = sys.platform == 'win32'

Let's create a minimum buildout that uses the current
plone.recipe.zope2instance::

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
    <zodb_db temporary>
        # Temporary storage database (for sessions)
        <temporarystorage>
          name temporary storage for sessioning
        </temporarystorage>
        mount-point /temp_folder
        container-class Products.TemporaryFolder.TemporaryContainer
    </zodb_db>
    python-check-interval 1000

We should have a blobstorage directory::

    >>> ls('var')
    d  blobstorage
    d  cache
    d  filestorage
    d  instance
    d  log

The blobstorage directory should only be readable by the current user,
otherwise you get a warning when the zope instance starts up.  The
(POSIX) path mode bits should be 0700::

    >>> WINDOWS or (os.stat(os.path.join('var', 'blobstorage')).st_mode & 0o077) == 0
    True


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


Custom storage wrapper
======================

To add custom configuration around the storage,
use the `storage-wrapper` option::

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
    ... storage-wrapper =
    ...   <foo>
    ...   %%s
    ...   </foo>
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

Now zope.conf should include the custom storage wrapper::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    ...
    <zodb_db main>
        ...
        <foo>
            # Blob-enabled FileStorage database
            ...
        </foo>
        ...
    </zodb_db>
    ...
    <BLANKLINE>


Custom Event log
================

`event-log-custom` is only supported for ZServer (Python 2 only).


Mailing logger
==============

`mailinglogger` is only supported for ZServer (Python 2 only).


Custom access log
=================

`access-log-custom`  is only supported for ZServer (Python 2 only).


Custom site.zcml file
=====================

`site-zcml` is a new option that allows you to create a custom site.zcml file.
When this option is used the `zcml` option is ignored. Let's try it::

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
    ... # the zcml option will be ignored when a site-zcml option is given
    ... zcml =
    ...       test.example
    ...
    ... site-zcml =
    ...       <configure xmlns="http://namespaces.zope.org/zope"
    ...                  xmlns:five="http://namespaces.zope.org/five">
    ...           <include package="Products.Five" />
    ...           <meta:redefinePermission from="zope2.Public" to="zope.Public" />
    ...           <include package="test.example" />
    ...       </configure>
    ...
    ... ''' % options)

Let's run the buildout::

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

    >>> WINDOWS or "Generated interpreter" in output
    True

Now let's check that we have a zope instance, with the custom site.zcml::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'site.zcml')) as fd:
    ...     print(fd.read())
    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:five="http://namespaces.zope.org/five">
        <include package="Products.Five" />
        <meta:redefinePermission from="zope2.Public" to="zope.Public" />
        <include package="test.example" />
    </configure>
    <BLANKLINE>


Environment Variables
=====================

We can specify environment variables for Zope.  Sometimes it is
useful to set the TZ variable if our instance will be moving
between several servers::

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
    ... environment-vars = TZ US/Eastern
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

Our environment variables should be set now::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    ...
    <environment>
      TZ US/Eastern
    CHAMELEON_CACHE .../var/cache
    </environment>
    ...

Now let's add several environment variables::

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
    ... environment-vars =
    ...     TZ US/Eastern
    ...     TMP /var/tmp
    ...     DISABLE_PTS True
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

Our environment variables should be set now::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> import re
    >>> env_vars = re.compile(r"<environment>\n\s*(?P<vars>.*)\n</environment>", re.M | re.S)
    >>> print(re.search(env_vars, zope_conf).group('vars'))
    TZ US/Eastern
    TMP /var/tmp
    DISABLE_PTS True
    CHAMELEON_CACHE .../var/cache

Several all on one line::

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
    ... template-cache = off
    ... environment-vars = TZ US/Eastern TMP /var/tmp DISABLE_PTS True
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

Our environment variables should be set now::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> re.search(env_vars, zope_conf).group('vars')
    'TZ US/Eastern\nTMP /var/tmp\nDISABLE_PTS True'


HTTP server
===========

Http-server options are only supported for ZServer (Python 2 only).


Edge Cases
==========

Some Linux distributions of Zope2 don't have the windows scripts.
Let's run a minimal buildout without them to make sure
we don't error::

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

Relative paths in scripts
=========================

The recipe supports the generation of scripts with relative paths.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... relative-paths = true
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... eggs =
    ... user = me:me
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

    >>> if not WINDOWS:
    ...     with open(join('bin', 'instance')) as fd:
    ...         value = fd.read()
    ... else:
    ...     value = ""
    >>> WINDOWS or 'base' in value and '__file__' in value
    True

Custom Zope Conf
=================

`zope-conf` is an option that allows you to use a specific Zope config file.

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
    ... zope-conf = /some/path/my.conf
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

We should have a zope instance script with the custom config file::

    >>> if not WINDOWS:
    ...     with open(join('bin', 'instance')) as fd:
    ...         value = fd.read()
    ... else:
    ...     value = ""
    >>> WINDOWS or 'plone.recipe.zope2instance.ctl.main(' in value and "['-C', '/some/path/my.conf', '-p', '" in value and "/bin/interpreter', '-w', '" in value and "etc/wsgi.ini']" in value
    True

Custom Zope Conf Imports
========================
`zope-conf-imports` is an option that allows you to import python packages that
define custom zope.conf sections using ZConfig API.

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
    ... zope-conf-imports =
    ...   mailinglogger
    ...   eea.graylogger
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

We should have a zope instance, with custom imports::

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %import mailinglogger
    %import eea.graylogger
    %define INSTANCEHOME .../sample-buildout/parts/instance
    ...
    <BLANKLINE>

Custom WSGI configuration
=========================

`wsgi` is an option that allows you to use a specific WSGI config file.

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
    ... wsgi = /some/path/service.ini
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

We should have a zope instance script with the custom config file::


    >>> if not WINDOWS:
    ...     with open(join('bin', 'instance')) as fd:
    ...         value = fd.read()
    ... else:
    ...     value = ""
    >>> WINDOWS or 'plone.recipe.zope2instance.ctl.main(' in value and "'-w', '/some/path/service.ini']" in value
    True

Resources directory
===================

`resources` is an option that allows you to register a
plone.app.theming resources directory.

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
    ... resources = ${buildout:directory}/myresources
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

The directory should have been generated, and zope config created::

    >>> 'myresources' in os.listdir(os.curdir)
    True
    >>> includes_path = join('parts', 'instance', 'etc', 'package-includes')
    >>> ls(includes_path)
    -  998-resources-configure.zcml
    >>> with open(os.path.join(includes_path, '998-resources-configure.zcml')) as fd:
    ...    print(fd.read().replace('\\', '/'))
    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:plone="http://namespaces.plone.org/plone">
        <include package="plone.resource" file="meta.zcml"/>
        <plone:static directory=".../sample-buildout/myresources"/>
    </configure>


Locales directory
===================

`locales` is an option that allows you to register a
plone.app.theming locales directory.

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
    ... locales = ${buildout:directory}/mylocales
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

The directory should have been generated, and zope config created::

    >>> 'mylocales' in os.listdir(os.curdir)
    True
    >>> includes_path = join('parts', 'instance', 'etc', 'package-includes')
    >>> ls(includes_path)
    -  001-locales-configure.zcml
    >>> with open(os.path.join(includes_path, '001-locales-configure.zcml')) as fd:
    ...    print(fd.read().replace('\\', '/'))
    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:i18n="http://namespaces.zope.org/i18n">
        <i18n:registerTranslations directory=".../sample-buildout/mylocales" />
    </configure>


Initialization
==============

`initialization` is an option that allows you to add custom Python
code to the initialization process.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... eggs = waitress
    ... user = me:me
    ... initialization =
    ...     print('Initialization complete! Hello %%(user)s!')
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

We should see the given initialization commands included in the instance
script::

    >>> if not WINDOWS:
    ...     with open(os.path.join(sample_buildout, 'bin', 'instance')) as fd:
    ...         instance = fd.read()
    ... else:
    ...     instance = ""
    >>> WINDOWS or "print('Initialization complete! Hello me:me!')" in instance
    True

    >>> waitress_path = os.path.join(sample_buildout, 'bin', 'waitress-serve')
    >>> if WINDOWS:
    ...     waitress_path += '-script.py'
    >>> with open(waitress_path) as fd:
    ...     waitress = fd.read()
    >>> "print('Initialization complete! Hello me:me!')" in waitress
    True


Exceptions debug mode
=====================
`debug-exceptions` disables exception views including
``standard_error_message`` and acts as a debugging aid during development.

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
    ... debug-exceptions = on
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

Now zope.conf should include the debug-exceptions configuration:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'zope.conf')) as fd:
    ...     zope_conf = fd.read()
    >>> zope_conf = zope_conf.replace('\\', '/')
    >>> print(zope_conf)
    %define INSTANCEHOME .../sample-buildout/parts/instance
    ...
    debug-exceptions on
    ...
    <BLANKLINE>
