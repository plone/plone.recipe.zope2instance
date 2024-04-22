===========================
Test wsgi instance creation
===========================

Test default configuration
==========================

    >>> from __future__ import print_function
    >>> from zc.buildout.testing import *
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

    >>> WINDOWS or "Generated script '" in output and 'instance' in output
    True


We should have an instance part, with a basic zope.conf::

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

The buildout has also created an INI file containing the waitress configuration:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as fd:
    ...     wsgi_ini = fd.read()
    >>> WINDOWS or 'fast-listen = 0.0.0.0:8080' in wsgi_ini
    True

    >>> WINDOWS or 'use = egg:plone.recipe.zope2instance#main' in wsgi_ini
    True

    >>> not WINDOWS or 'use = egg:waitress#main' in wsgi_ini
    True

    >>> print(wsgi_ini.replace('\\', '/'))
    [server:main]
    ...
    <BLANKLINE>
    [app:zope]
    use = egg:Zope#main
    zope_conf = .../sample-buildout/parts/instance/etc/zope.conf
    <BLANKLINE>
    [filter:translogger]
    use = egg:Paste#translogger
    setup_console_handler = False
    ...
    [pipeline:main]
    pipeline =
        translogger
        egg:Zope#httpexceptions
        zope
    <BLANKLINE>
    [loggers]
    keys = root, plone, waitress.queue, waitress, wsgi
    <BLANKLINE>
    [handlers]
    keys = console, accesslog, eventlog
    <BLANKLINE>
    [formatters]
    keys = generic, message
    <BLANKLINE>
    [logger_root]
    level = INFO
    handlers = console, eventlog
    <BLANKLINE>
    [logger_plone]
    level = INFO
    handlers = eventlog
    qualname = plone
    <BLANKLINE>
    [logger_waitress.queue]
    level = INFO
    handlers = eventlog
    qualname = waitress.queue
    propagate = 0
    <BLANKLINE>
    [logger_waitress]
    level = INFO
    handlers = eventlog
    qualname = waitress
    <BLANKLINE>
    [logger_wsgi]
    level = INFO
    handlers = accesslog
    qualname = wsgi
    propagate = 0
    <BLANKLINE>
    [handler_console]
    class = StreamHandler
    args = (sys.stderr,)
    level = NOTSET
    formatter = generic
    <BLANKLINE>
    [handler_accesslog]
    class = FileHandler
    args = (r'.../sample-buildout/var/log/instance-access.log', 'a')
    kwargs = {}
    level = INFO
    formatter = message
    <BLANKLINE>
    [handler_eventlog]
    class = FileHandler
    args = (r'.../sample-buildout/var/log/instance.log', 'a')
    kwargs = {}
    level = NOTSET
    formatter = generic
    <BLANKLINE>
    [formatter_generic]
    format = %(asctime)s %(levelname)-7.7s [%(name)s:%(lineno)s][%(threadName)s] %(message)s
    <BLANKLINE>
    [formatter_message]
    format = %(message)s

Custom WSGI options
==================

Let's create another buildout configuring a custom port and a custom number of workers::

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
    ... http-address = localhost:6543
    ... http-fast-listen = on
    ... threads = 3
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

The buildout has updated our INI file:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as fd:
    ...     wsgi_ini = fd.read()
    >>> WINDOWS or 'fast-listen = localhost:6543' in wsgi_ini
    True

    >>> WINDOWS or 'threads = 3' in wsgi_ini
    True

You can also specify multiple http-address and/or specify only the port
(the host part will be assumed to be 0.0.0.0):

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
    ... http-address =
    ...     localhost:6543
    ...     127.0.0.1:6544
    ...     8080
    ... ''' % options)
    >>> _ = system(join('bin', 'buildout'))

The buildout has updated our INI file:

    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as fd:
    ...     wsgi_ini = fd.read()
    >>> WINDOWS or 'fast-listen = localhost:6543 127.0.0.1:6544 0.0.0.0:8080' in wsgi_ini
    True

Custom logging
==============

We want file based logging, i.e. event.log and access.log (ZServers Z2.log).
Let's create a buildout:

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
    ... access-log = var/log/foo.log
    ... event-log = var/log/bar.log
    ... z2-log-level = DEBUG
    ... event-log-level = ERROR
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

The buildout has updated our INI file:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as fd:
    ...     wsgi_ini = fd.read()
    >>> print(wsgi_ini.replace('\\', '/'))
    [server:main]
    ...
    [logger_root]
    level = ERROR
    handlers = console, eventlog
    <BLANKLINE>
    [logger_plone]
    level = ERROR
    handlers = eventlog
    qualname = plone
    <BLANKLINE>
    [logger_waitress.queue]
    level = INFO
    handlers = eventlog
    qualname = waitress.queue
    propagate = 0
    <BLANKLINE>
    [logger_waitress]
    level = ERROR
    handlers = eventlog
    qualname = waitress
    <BLANKLINE>
    [logger_wsgi]
    level = DEBUG
    handlers = accesslog
    qualname = wsgi
    propagate = 0
    ...
    [handler_accesslog]
    class = FileHandler
    args = (r'var/log/foo.log', 'a')
    kwargs = {}
    level = DEBUG
    formatter = message
    <BLANKLINE>
    [handler_eventlog]
    class = FileHandler
    args = (r'var/log/bar.log', 'a')
    kwargs = {}
    level = NOTSET
    formatter = generic
    ...

Next we want to disable access logging (but keep an event log file):

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
    ... access-log = disable
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

The buildout has updated our INI file:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as fd:
    ...     wsgi_ini = fd.read()
    >>> print(wsgi_ini)
    [server:main]
    ...
    [pipeline:main]
    pipeline =
        egg:Zope#httpexceptions
        zope
    ...

Now we also want to disable event logging:

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
    ... access-log = disable
    ... event-log = disable
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Uninstalling instance" in output
    True

    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

The buildout has updated our INI file:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as fd:
    ...     wsgi_ini = fd.read()
    >>> print(wsgi_ini)
    [server:main]
    ...
    [pipeline:main]
    pipeline =
        egg:Zope#httpexceptions
        zope
    ...
    [logger_root]
    level = INFO
    handlers = console
    <BLANKLINE>
    [logger_plone]
    level = INFO
    handlers =
    qualname = plone
    <BLANKLINE>
    [logger_waitress.queue]
    level = INFO
    handlers = eventlog
    qualname = waitress.queue
    propagate = 0
    <BLANKLINE>
    [logger_waitress]
    level = INFO
    handlers =
    qualname = waitress
    ...

Sentry support
==============

We want to sent logging events to Sentry.
Let's create a buildout:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... eggs =
    ...     plone.recipe.zope2instance[sentry]
    ... user = me:me
    ... sentry_dsn = https://f00ba4ba2@my.sentry.server/9999
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> if "Uninstalling instance" not in output or "Installing instance" not in output:
    ...    print(output)
    >>> if not WINDOWS and "Generated script" not in output:
    ...     print(output)
    
The buildout has updated our INI file:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as fd:
    ...     wsgi_ini = fd.read()
    >>> print(wsgi_ini)
    [server:main]
    ...
    [filter:sentry]
    use = egg:plone.recipe.zope2instance#sentry
    dsn = https://f00ba4ba2@my.sentry.server/9999
    level = INFO
    event_level = ERROR
    ignorelist =
    max_value_length =
    ...
    [pipeline:main]
    pipeline =
        translogger
        egg:Zope#httpexceptions
        sentry
        zope
    <BLANKLINE>
    [loggers]
    ...

Let's update our buildout with some Sentry options:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ... find-links = %(sample_buildout)s/eggs
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... eggs =
    ...     plone.recipe.zope2instance[sentry]
    ... user = me:me
    ... sentry_dsn = https://f00ba4ba2@my.sentry.server/9999
    ... sentry_level = DEBUG
    ... sentry_event_level = WARNING
    ... sentry_ignore = waitress.queue foo
    ... sentry_max_value_length = 2048
    ... ''' % options)

Let's run it::

    >>> output = system(join('bin', 'buildout'))
    >>> "Installing instance" in output
    True

    >>> WINDOWS or "Generated script" in output
    True

The buildout has updated our INI file:

    >>> instance = os.path.join(sample_buildout, 'parts', 'instance')
    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as fd:
    ...     wsgi_ini = fd.read()
    >>> print(wsgi_ini)
    [server:main]
    ...
    [filter:sentry]
    use = egg:plone.recipe.zope2instance#sentry
    dsn = https://f00ba4ba2@my.sentry.server/9999
    level = DEBUG
    event_level = WARNING
    ignorelist = waitress.queue foo
    max_value_length = 2048
    ...
    [pipeline:main]
    pipeline =
        translogger
        egg:Zope#httpexceptions
        sentry
        zope
    <BLANKLINE>
    [loggers]
    ...

Custom pipeline
===============

The recipe can configure custom pipelines in the ``wsgi.ini``::

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
    ... pipeline =
    ...     foo
    ...     bar
    ... ''' % options)

Let's run it::

    >>> print(system(join('bin', 'buildout'))),
    Uninstalling instance.
    Installing instance.
    ...

The buildout has updated our INI file and we can see that we have a custom pipeline:

    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as f:
    ...     wsgi_ini = f.read()
    >>> print(wsgi_ini)
    [server:main]
    ...
    [pipeline:main]
    pipeline =
        foo
        bar
        zope
    <BLANKLINE>
    [loggers]
    ...


With repoze.profile middleware
==============================

The recipe can configure custom pipelines in the ``wsgi.ini``::

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
    ... profile = on
    ... ''' % options)

Let's run it::

    >>> print(system(join('bin', 'buildout'))),
    Uninstalling instance.
    Installing instance.
    ...

The buildout has updated our INI file and we can see that we have a custom pipeline:

    >>> with open(os.path.join(instance, 'etc', 'wsgi.ini')) as f:
    ...     wsgi_ini = f.read()
    >>> print(wsgi_ini)
    [server:main]
    ...
    [filter:profile]
    use = egg:repoze.profile
    ...
    discard_first_request = true
    path = /__profile__
    flush_at_shutdown = true
    unwind = false
    <BLANKLINE>
    [pipeline:main]
    pipeline =
        translogger
        egg:Zope#httpexceptions
        profile
        zope
    <BLANKLINE>
    [loggers]
    ...


# END OF TEST
