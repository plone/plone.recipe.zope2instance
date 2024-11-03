Introduction
============

.. image:: http://img.shields.io/pypi/v/plone.recipe.zope2instance.svg
   :target: https://pypi.org/project/plone.recipe.zope2instance

.. image:: http://img.shields.io/travis/plone/plone.recipe.zope2instance.svg
   :target: https://travis-ci.org/plone/plone.recipe.zope2instance

.. image:: https://github.com/plone/plone.recipe.zope2instance/workflows/Test/badge.svg?branch=master
   :target: https://github.com/plone/plone.recipe.zope2instance/actions?query=workflow%3ATest+branch%3Amaster

This recipe creates and configures a Zope instance in parts.
(Despite its name it nowadays only works for Zope 4+.) It also
installs a control script, which is like zopectl, in the bin/ directory.
The name of the control script is the name of the part in buildout.
By default various runtime and log information will be stored inside the var/
directory.

You can use it with a part like this::

  [instance]
  recipe = plone.recipe.zope2instance
  user = admin:admin
  http-address = 8080
  eggs = my.distribution
  zcml = my.distribution

.. contents:: **Contents**


Options
=======

Common options
--------------

eggs
  The list of distributions you want to make available to the instance.

zcml
  Install ZCML slugs for the distributions listed, separated by whitespace. You
  can specify the type of slug by appending '-' and the type of slug you want
  to create. Some examples: ``my.distribution`` ``my.distribution-meta``.

http-address
  Set the address of the HTTP server.
  Can be either a port or a socket address.
  Defaults to 0.0.0.0:8080.

ip-address
  The default IP address on which Zope's various server protocol
  implementations will listen for requests. If this is unset, Zope will listen
  on all IP addresses supported by the machine. This directive can be
  overridden on a per-server basis in the servers section. Defaults to not
  setting an ip-address. Used for ZServer only, not WSGI.

threads
  Specify the number of worker threads used to service requests.
  The default is 4 for WSGI (since this is the waitress default) and 2 for ZServer.

zodb-cache-size
  Set the ZODB cache size, i.e. the number of objects which the ZODB cache
  will try to hold. Defaults to 30000.

zserver-threads
  Deprecated, use `threads` instead.
  Specify the number of threads that Zope's ZServer web server will use to
  service requests. The recipes default is 2. Used for ZServer only, not WSGI.

environment-vars
  Define arbitrary key-value pairs for use as environment variables during
  Zope's run cycle. Example::

    environment-vars =
      TZ US/Eastern
      zope_i18n_allowed_languages en
      zope_i18n_compile_mo_files true

initialization
   Specify some Python initialization code to include within the generated
   ``sitecustomize.py`` script (Buildout >= 1.5) or within the instance script
   (Buildout < 1.5). This is very limited. In particular, be aware that leading
   whitespace is stripped from the code given. *added in version 4.2.14*

wsgi
   By default this recipe creates a Python script that uses ``waitress`` as a
   WSGI server. When running Python 2 you can disable WSGI and use ZServer by
   setting ``wsgi = off`` and including ZServer in the ``eggs`` specification
   list. Example::

     wsgi = off
     eggs =
       ...
       ZServer

   You can use other PasteDeploy-compatible WSGI servers by passing a path
   to a WSGI configuration file here and including the WSGI server's egg in the
   ``eggs`` specification. Example::

     wsgi = ${buildout:directory}/etc/gunicorn.ini
     eggs =
       ...
       gunicorn

   The WSGI configuration file will not be created for you in this case,
   unlike the built-in ``waitress`` support. You have to provide it yourself.

max-request-body-size
   Specify the maximum request body size in bytes
   The default is 1073741824 (since this is the waitress default)


Theme resources
---------------

Please refer to `<https://pypi.org/project/plone.resource>`_ for more
details and setup instructions.

resources
  Specify a central resource directory. Example::

    resources = ${buildout:directory}/resources

Locales
-------

locales
  Specify a locales directory. Example::

    locales = ${buildout:directory}/locales

This registers a locales directory with extra or different translations.
If you want to override a few translations from the `plone` domain in the
English language, you can add a ``en/LC_MESSAGES/plone.po`` file in this
directory, with standard headers at the top, followed by something like
this::

  #. Default: "You are here:"
  msgid "you_are_here"
  msgstr "You are very welcome here:"

Translations for other message ids are not affected and will continue
to work.

Development options
-------------------

verbose-security
  Set to `on` to turn on verbose security (and switch to the Python security
  implementation). Defaults to `off` (and the C security implementation).

debug-exceptions
  WSGI only: set to ``on`` to disable exception views including
  ``standard_error_message``. Exceptions other than ``Unauthorized`` or
  ``ConflictError`` can then travel up into the WSGI stack. Use this option
  if you want more convenient error debugging offered by WSGI middleware
  such as the `werkzeug debugger
  <https://werkzeug.palletsprojects.com/en/0.15.x/debug/>`_. See the `Zope
  WSGI documentation <https://zope.readthedocs.io/en/latest/wsgi.html>`_ for
  examples.

profile
  Set to ``on`` enables `repoze.profile <https://github.com/repoze/repoze.profile>`_.
  Defaults to ``off``,
  If switched on there are further options prefixed with ``profile_`` to configure it as below.
  You will need to add the `repoze.profile` package, either by adding it to your eggs section directly or by using the extra `plone.recipe.zope2instance[profile]`.

profile_log_filename
  Filename of the raw profile data.
  Default to ``profile-SECTIONNAME.raw``.
  This file contains the raw profile data for further analysis.

profile_cachegrind_filename
  If the package ``pyprof2calltree`` is installed, another file is written.
  It is meant for consumation with any cachegrind compatible application.
  Defaults to ``cachegrind.out.SECTIONNAME``.

profile_discard_first_request
  Defaults to ``true``.
  See `repoze.profile docs <https://repozeprofile.readthedocs.io/en/latest/#configuration-via-python>`_ for details.

profile_path
  Defaults to ``/__profile__``.
  The path for through the web access to the last profiled request.

profile_flush_at_shutdown
  Defaults to ``true``.
  See `repoze.profile docs <https://repozeprofile.readthedocs.io/en/latest/#configuration-via-python>`_ for details.

profile_unwind
  Defaults to ``false``.
  See `repoze.profile docs <https://repozeprofile.readthedocs.io/en/latest/#configuration-via-python>`_ for details.


Direct storage
--------------

If you have only one application process, it can open the database files
directly without running a database server process.

file-storage
  The filename where the ZODB data file will be stored.
  Defaults to `${buildout:directory}/var/filestorage/Data.fs`.

blob-storage
  The name of the directory where the ZODB blob data will be stored, defaults
  to `${buildout:directory}/var/blobstorage`.

Basic ZEO storage
-----------------

If you want multiple application processes you need to run a separate
database server process and connect to it, either via ZEO or RelStorage.

zeo-address
  Set the address of the ZEO server. Defaults to 8100. You can set
  more than one address (white space delimited). Alternative addresses will
  be used if the primary address is down.

zeo-client
  Set to 'on' to make this instance a ZEO client. In this case, setting the
  zeo-address option is required, and the file-storage option has no effect.
  To set up a ZEO server, you can use the plone.recipe.zeoserver recipe.
  Defaults to 'off'.

blob-storage
  The location of the blob zeocache, defaults to `var/blobcache`. If
  `shared-blob` is on it defaults to `${buildout:directory}/var/blobstorage`.

shared-blob
  Defaults to `off`. Set this to `on` if the ZEO server and the instance have
  access to the same directory. Either by being on the same physical machine or
  by virtue of a network file system like NFS. Make sure this instances
  `blob-storage` is set to the same directory used for the ZEO servers
  `blob-storage`. In this case the instance will not stream the blob file
  through the ZEO connection, but just send the information of the file
  location to the ZEO server, resulting in faster execution and less memory
  overhead.

zeo-client-read-only-fallback
  A flag indicating whether a read-only remote storage should be acceptable as
  a fallback when no writable storages are available. Defaults to false.

read-only
  Set zeo client as read only *added in version 4.2.12*

ZEO authentication
------------------

You need to activate ZEO auth on the server side as well, for this to work.
Without this anyone that can connect to the database servers socket can read
and write arbitrary data.

zeo-username
  Enable ZEO authentication and use the given username when accessing the
  ZEO server. It is obligatory to also specify a zeo-password.

zeo-password
  Password to use when connecting to a ZEO server with authentication
  enabled.

zeo-realm
  Authentication realm to use when authentication with a ZEO server. Defaults
  to 'ZEO'.

RelStorage
----------

Please refer to `<https://pypi.org/project/RelStorage>`_ for more details
and setup instructions.

rel-storage
  Allows to set a RelStorage instead of a FileStorage.

  Contains settings separated by newlines, with these values:

  - type: any database type supported (postgresql, oracle, mysql)
  - RelStorage specific keys, like `cache-servers` and `poll-interval`
  - all other keys are passed on to the database-specific RelStorage adapter.

  Example::

    rel-storage =
      type oracle
      dsn (DESCRIPTION=(ADDRESS=(HOST=s01))(CONNECT_DATA=(SERVICE_NAME=d01)))
      user tarek
      password secret

Logging
-------

In most cases you don't need to adjust any of this, you might want to adjust
log levels or configure `mailinglogger`.

event-log
  The filename of the event log. Defaults to ${buildout:directory}/var/log/${partname}.log
  Setting this value to 'disable' will make the <eventlog> section to be omitted,
  disabling logging events by default to a .log file.

event-log-level
  Set the level of the console output for the event log. Level may be any of
  CRITICAL, ERROR, WARN, INFO, DEBUG, or ALL. Defaults to INFO.

event-log-max-size
  Maximum size of event log file. Enables log rotation.
  Used for ZServer only, not WSGI.

event-log-old-files
  Number of previous log files to retain when log rotation is enabled.
  Defaults to 1. Used for ZServer only, not WSGI.

event-log-custom
  A custom section for the eventlog, to be able to use another
  event logger than `logfile`. Used for ZServer only, not WSGI.

mailinglogger
  A mailinglogger section added into the event log.
  Used for ZServer only, not WSGI. Example snippet::

    <mailing-logger>
      level error
      flood-level 10
      smtp-server smtp.mydomain.com
      from logger@mydomain.com
      to errors@mydomain.com
      subject [My domain error] [%(hostname)s] %(line)s
    </mailing-logger>

  You will need to add `mailinglogger` to your buildout's egg section to make this work.

access-log, z2-log
  The filename for the Z2 access log. Defaults to var/log/${partname}-Z2.log
  (var/log/${partname}-access.log) for WSGI).
  You can disable access logging by setting this value to 'disable'.
  For ZServer this will omit the `<logger access>` section in `zope.conf`.
  For WSGI, the logging handler will be a `NullHandler <https://docs.python.org/3/library/logging.handlers.html#nullhandler>`_.

access-log-level, z2-log-level
  Set the log level for the access log. Level may be any of CRITICAL, ERROR,
  WARN, INFO, DEBUG, or ALL. Defaults to WARN (INFO for WSGI).

access-log-max-size
  Maximum size of access log file. Enables log rotation.
  Used for ZServer only, not WSGI.

access-log-old-files
  Number of previous log files to retain when log rotation is enabled.
  Defaults to 1. Used for ZServer only, not WSGI.

access-log-custom
  Like `event-log-custom`, a custom section for the access logger, to be able
  to use another event logger than `logfile`. Used for ZServer only, not WSGI.

sentry_dsn
  Provide a Sentry DSN here to enable basic Sentry logging documented
  in `<https://docs.sentry.io/platforms/python/logging/>`_. You will need to add the
  Python Sentry SDK, either by adding it to your eggs section directly or by adding
  `plone.recipe.zope2instance[sentry]`.
  Available for WSGI only.

sentry_level
  Set the logging level for Sentry breadcrumbs.
  Available for WSGI only.

sentry_event_level
  Set the logging level for Sentry events.
  Available for WSGI only.

sentry_ignore
  Set the (space separated list of) logger names that are ignored by Sentry.
  Available for WSGI only.

sentry_max_value_length
  Set the maximum size of traceback messages sent to Sentry. If your tracebacks
  get truncated, increase this above the sentry-sdk default of 1024.
  Available for WSGI only.

Advanced logging options for WSGI
---------------------------------

For more complex logging configuration, the zope2instance recipe exposes the
underlaying `logging.handlers` functionality through the `access-log-handler`
and `event-log-handler` configuration options. This allows you to configure an
arbitrary logging handler for Python as defined in
`here <https://docs.python.org/3/library/logging.handlers.html>`_.

The supplementary options `event-log-args`, `event-log-kwargs` and
`access-log-args`, `access-log-kwargs` can be used for passing positional and
keyword arguments to the constructor of the underlaying handler.

access-log-handler
  The (dotted) name of an importable Python logging handler like
  `logging.handlers.RotatingFileHandler`.

  Default: `FileHandler`

access-log-args
  A python tuple which usually refers to the logging filename and opening mode
  of the file like `("access.log", "a")`.  Note that you a Python tuple with
  only one element (e.g. only the filename) must have a trailing comma like
  `("access.log", )` The `access-log-args` is used to specify the positional
  parameters for the logging handler configured through `access-log-handler`.

  Default: `(r"access.log", "a")`

access-log-kwargs
  A python dictionary used for passing keyword argument for the logging handler
  configured through `access-log-handler` e.g.  `{"when": "h", "interval": 1}`.

  Default: `{}`

event-log-handler
    Same as `access-log-handler` but for the configuration of the event log of Plone.

event-log-args
    Same as `access-log-args` but for the configuration of the event log of Plone.

event-log-kwargs
    Same as `access-log-kwargs` but for the configuration of the event log of Plone.

wsgi-logging-ini-template
  By default `plone.recipe.zope2instance` uses a hard-coded logging template for the
  generated WSGI configuration in `parts/<partname>/etc/wsgi.ini`. The template
  is defined as `wsgi_logging_ini_template` variable within the `recipe.py
  <https://github.com/plone/plone.recipe.zope2instance/blob/master/src/plone/recipe/zope2instance/recipe.py>`_
  file.

  You can override the template with a custom `wsgi_logging.ini` file using this option.
  All other default wsgi options will be untouched.

  Example::

      wsgi-logging-ini-template = /path/to/wsgi_logging.ini

  This option cannot be used together with the `wsgi-ini-template` option (see Advanced options: wsgi-ini-template)

Example (access log rotation based on file size)
++++++++++++++++++++++++++++++++++++++++++++++++

This example uses a `RotatingFileHandler` https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler
which rotates the access log when it becomes larger than 10 MB while keeping seven copies::

    access-log-handler = logging.handlers.RotatingFileHandler
    access-log-args  = (r"access.log", "a")
    access-log-kwargs = {"maxBytes": 10000000, "backupCount": 7}

Example (rotating of event log after each day)
++++++++++++++++++++++++++++++++++++++++++++++

This example uses a `TimedRotatingFileHandler` https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
for rotating the event log every 24 hours or one day::

    event-log-handler = logging.handlers.TimedRotatingFileHandler
    event-log-args = (r"event.log", )
    event-log-kwargs = {"when": "D", "interval": 1}

Load non-setuptools compatible Python libraries
-----------------------------------------------

products
  A list of paths where Zope 2 products are installed. The first path takes
  precedence in case the same product is found in more than one directory.
  Zope 2 products are deprecated and won't work any longer in a future version
  of Zope/Plone.

extra-paths
  A list of paths where additional Python packages are installed. The paths
  are searched in the given order after all egg and products paths.

Advanced ZCML options
---------------------

site-zcml
  If you want a custom `site.zcml` file, put its content here. If this option
  is used the `zcml` and `zcml-additional` options are ignored.

zcml-additional
  Extra ZCML statements that should be included in the generated `site.zcml`
  file.

Advanced ZEO options
--------------------

zeo-client-cache-size
  Set the size of the ZEO client cache. Defaults to '128MB'. The ZEO cache is
  a disk based cache shared between application threads. It is stored either in
  temporary files or, in case you activate persistent cache files with the
  option `client` (see below), in the folder designated by the `zeo-var`
  option.

zeo-client-client
  Set the persistent cache name that is used to construct the cache
  filenames. This enables the ZEO cache to persist across application restarts.
  Persistent cache files are disabled by default.

zeo-client-blob-cache-size
  Set the maximum size of the ZEO blob cache, in bytes.  If not set, then
  the cache size isn't checked and the blob directory will grow without bound.

zeo-client-blob-cache-size-check
  Set the ZEO check size as percent of `zeo-client-blob-cache-size` (for
  example, `10` for 10%). The ZEO cache size will be checked when this many
  bytes have been loaded into the cache. Defaults to 10% of the blob cache
  size. This option is ignored if `shared-blob` is enabled.

zeo-client-drop-cache-rather-verify
  Indicates that the cache should be dropped rather than verified when
  the verification optimization is not available (e.g. when the ZEO server
  restarted). Defaults to 'False'.

zeo-storage
  Set the storage number of the ZEO storage. Defaults to '1'.

zeo-var
  Used in the ZEO storage snippets to configure the ZEO var folder, which
  is used to store persistent ZEO client cache files. Defaults to the system
  temporary folder.

Advanced options
----------------

wsgi-ini-template
  By default `plone.recipe.zope2instance` uses a hard-coded template for the
  generated WSGI configuration in `parts/<partname>/etc/wsgi.ini`. The template
  is defined as `wsgi_ini_template` variable within the `recipe.py
  <https://github.com/plone/plone.recipe.zope2instance/blob/master/src/plone/recipe/zope2instance/recipe.py>`_
  file.

  You can override the template with a custom template file using this option.

  Example::

      wsgi-ini-template = /path/to/wsgi_template.ini

  The available variables for variable substition can be found within the existing template (see above).

asyncore-use-poll
  By default `false`. If you want the `waitress.asyncore.loop` flag to use poll()
  instead of the default select() set to `true`.

before-storage
  Wraps the base storage in a "before storage" which sets it in
  read-only mode from the time given (or "now" for the current time).

  This option is normally used together with demo-storage for a
  normally running site in order for changes to be made to the
  database.

client-home
  Sets the clienthome for the generated instance.
  Defaults to ${buildout:directory}/var/<name of the section>.

clear-untrusted-proxy-headers
  This tells Waitress to remove any untrusted proxy headers
  ("Forwarded", "X-Forwarded-For", "X-Forwarded-By",
  "X-Forwarded-Host", "X-Forwarded-Port", "X-Forwarded-Proto").
  The default in waitress 1 is false, but waitress 2 changes this to true.
  We explicitly default to false.
  When you set it to true, you may need to set other ``wsgi.ini`` options like
  ``trusted_proxy_headers`` and ``trusted_proxy``.
  Setting those is not supported by the recipe yet.
  Used for WSGI only, not ZServer.

default-zpublisher-encoding
  This controls what character set is used to encode unicode data that reaches
  ZPublisher without any other specified encoding. This defaults to 'utf-8'.
  Plone requires this to be set to `utf-8`.

demo-storage
  If 'on' it enables the demo storage. By default, this is a
  memory-based storage option; changes are not persisted (see the
  demo-file-storage option to use a persistent storage for changes
  made during the demonstration).

  To use with a base storage option configured with a blob-storage,
  you must set a demo-blob-storage.

demo-file-storage
  If provided, the filename where the ZODB data file for changes
  committed during a demonstration will be stored.

demo-blob-storage
  If provided, the name of the directory where demonstration ZODB blob
  data will be stored.

  This storage may be connected to a demonstration file storage, or
  used with the default memory-based demo storage (in this case you
  might want to use a temporary directory).

storage-wrapper
  Template for arbitrary configuration to be wrapped around the main storage.
  %s will be replaced with the existing storage configuration.

effective-user
  The name of the effective user for the Zope process. Defaults to not setting
  an effective user.

enable-product-installation
  Enable the persistent product registry by setting this to ``on``. By default
  the registry is turned ``off``. Enabling the registry is deprecated.

ftp-address
  Give a port for the FTP server. This enables the FTP server.
  Used for ZServer only, not WSGI.

http-force-connection-close
  Set to `on` to enforce Zope to set ``Connection: close header``.
  This is useful if for example a 304 leaves the connection open with
  Varnish in front and Varnish tries to reuse the connection.

http-fast-listen
  Set to `off` to defer opening of the HTTP socket until the end of the Zope
  startup phase. Defaults to on.

icp-address
  Give a port for the ICP server. This enables the ICP server.
  Used for ZServer only, not WSGI.

import-directory
  Used to configure the import directory for instance.
  Defaults to `<client-home>/import`.

port-base
  Offset applied to the port numbers used for ZServer configurations. For
  example, if the http-server port is 8080 and the port-base is 1000, the HTTP
  server will listen on port 9080. This makes it easy to change the complete
  set of ports used by a Zope server process. Zope defaults to 0.

python-check-interval
  An integer telling the Python interpreter to check for asynchronous events
  every number of instructions. This affects how often thread switches occur.
  Defaults to 1000.

relative-paths
  Set this to `true` to make the generated scripts use relative
  paths. You can also enable this in the `[buildout]` section.

scripts
  Add this parameter with no arguments to suppress script generation.
  Otherwise (i.e. without this parameter), scripts for packages added
  to the `eggs` parameter will be generated. You may also configure
  per package. E.g.::

    [instance]
    recipe = plone.recipe.zope2instance
    eggs =
      Plone
      mr.migrator
      my.package
    scripts = my_package_script

  In the above example, only `my_package_script` will be generated. Keep in
  mind that the egg containing the script (``my.package`` in the example) must
  be listed explicitly in the eggs option, even if it is a dependency of an
  already listed egg.

template-cache
  Used to configure the cache for page-template files. Chameleon will write
  compile page-templates into this directory and use it as a cache.
  See https://chameleon.readthedocs.io/en/latest/configuration.html for more info.
  Valid options are off or on or a directory-location.
  Defaults to ${buildout:directory}/var/cache (it also confirms to what var is set to).

var
  Used to configure the base directory for all things going into var.
  Defaults to ${buildout:directory}/var.

webdav-address
  Give a port for the WebDAV server.  This enables the WebDAV server.
  Used for ZServer only, not WSGI.

webdav-force-connection-close
  Valid options are off and on. Defaults to off.
  Used for ZServer only, not WSGI.

pipeline
   The main application pipeline served by the wsgi server.
   By default the pipeline is::

     translogger
     egg:Zope#httpexceptions
     zope

   The ``translogger`` line in the pipeline will be removed
   if ``z2-log`` is set to ``disabled`` or if it is not set
   and ``access-log`` is set to ``disabled`` (case insensitive).
   Used for WSGI only, not ZServer.

zlib-storage
  Adds support for file compression on a file storage database. The
  option accepts the values 'active' (compress new records) or
  'passive' (do not compress new records). Both options support
  already compressed records.

  You can use the 'passive' setting while you prepare a number of
  connected clients for compressed records.

zodb-cache-size-bytes
  Set the ZODB cache sizes in bytes. This feature is still experimental.

zodb-temporary-storage
  If given Zope's default temporary storage definition will be replaced by
  the lines of this parameter. If set to "off" or "false", no temporary storage
  definition will be created. This prevents startup issues for basic Zope 4
  sites as it does not ship with the required packages by default anymore.

zope-conf
  A relative or absolute path to a `zope.conf` file. If this is given, many of
  the options in the recipe will be ignored.

zope-conf-imports
  You can define custom sections within zope.conf using the ZConfig API.
  But, in order for Zope to understand your custom sections, you'll have to
  import the python packages that define these custom sections using `%import`
  syntax.

  Example::

    zope-conf-imports =
      mailinglogger
      eea.graylogger

zope-conf-additional
  Give additional lines to `zope.conf`. Make sure you indent any lines after
  the one with the parameter.

  Example::

    zope-conf-additional =
      locale fr_FR
      http-realm Slipknot

zopectl-umask
  Manually set the umask for the zopectl process.

  Example::

    zopectl-umask = 002

http-header-max-length
  Manually set the maximum size of received HTTP header being processed by Zope.
  The request is discarded and considered as a DoS attack if the header size exceeds
  this limit. Default: 8192. Used for ZServer only, not WSGI.

  Example::

    http-header-max-length = 16384


The generated control script
============================

Windows
-------

On the windows platform the ``bin/instance`` script as described below will not be generated, because it uses a Unix specific implementation.

To run Plone start it with::

  .\bin\runwsgi.exe -v .\parts\etc\wsgi.ini

Or for development in debug mode use::

  .\bin\runwsgi.exe -v .\parts\etc\wsgi.ini

The documentation for the extended Zope control script below does not apply.


The `debug`, `console` and `run` commands
-----------------------------------------

The extended Zope control script installed by this recipe, usually
`bin/instance` by convention, offers a `debug` command and another
`run` command.  The `debug` command starts an interactive Python
prompt with the Zope application available via the `app` name.
Similarly, the `run` command accepts a Python script as an argument
that will be run under the same conditions.

These commands have also been extended to set up a more complete
environment. Specifically, these commands set up a REQUEST, log in
the AccessControl.SpecialUsers.system user, and may traverse to an
object, such as a CMF portal. This environment set up is controlled
with following options::

    -R/--no-request -- do not set up a REQUEST.
    -L/--no-login -- do not login the system user.
    -O/--object-path <path> -- Traverse to <path> from the app
                               and make available as `obj`.

Note that these options must come before the script name,
e.g. `bin/instance -RLOPlone/front-page debug`

The `console` command is similar to the fg command, but it does not
create a subprocess to start up Zope. This is useful for two
use cases. First, the supervisor program, to supervise long running
processes like a Zope, require the process not to fork away, so that
supervisor can control it.
Second, IDEs like WingIDE and PyCharm support debugging running
processes from within. For this to work, the process should also
not fork away.

Developing your own control script commands
-------------------------------------------

Third-party distributions may add additional commands to the control script by
installing a 'plone.recipe.zope2instance.ctl' entry point. For example,
an egg called MyDist could include a module called mymodule with the
following custom command::

    def foo(self, *args)
        """Help message here"""
        print 'foo'

It would then install the foo method as a command for the control script using
the following entry point configuration in setup.py::

    entry_points="""
    [plone.recipe.zope2instance.ctl]
    foo = mymodule:foo
    """

This would allow invoking the foo method by running `bin/instance foo`
(assuming the instance control script was installed by a buildout part
called `instance`.) The entry point is invoked with the following
parameters:

  self
    An instance of plone.recipe.zope2instance.ctl.AdjustedZopeCmd.
  args
    Any additional arguments that were passed on the command line.

Known issues
------------

* the ``restart`` command will not function reliably if you run the buildout
  while the Zope instance is still running. In those cases, always use
  ``stop`` followed by ``start`` to restart the Zope instance.

Reporting bugs or asking questions
==================================

Please use the bug tracker in this repository at
https://github.com/plone/plone.recipe.zope2instance/issues for questions and
bug reports.

