Introduction
============

.. image:: http://img.shields.io/pypi/v/plone.recipe.zope2instance.svg
   :target: https://pypi.python.org/pypi/plone.recipe.zope2instance

.. image:: http://img.shields.io/travis/plone/plone.recipe.zope2instance.svg
   :target: https://travis-ci.org/plone/plone.recipe.zope2instance

This recipe creates and configures a Zope 2 instance in parts. It also
installs a control script, which is like zopectl, in the bin/ directory.
The name of the control script is the the name of the part in buildout.
By default various runtime and log information will be stored inside the var/
directory.

*Note: This recipe is not intended to setup a Zope 2 WSGI based instance and
will not work for this use-case. There's no special recipe required to setup
WSGI any longer and you can use simple template recipes instead.*

You can use it with a part like this::

  [instance]
  recipe = plone.recipe.zope2instance
  user = admin:admin
  http-address = 8080
  eggs = my.distribution
  zcml = my.distribution

.. ATTENTION::
   This release is targeted at Zope 2.12+ and Python 2.6. If you are using
   this recipe with earlier versions of Zope or Python, you should use one
   of the releases from the 3.x series.

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
  Give a port for the HTTP server. Defaults to 8080.  Set to an empty
  string to disable the HTTP server.  You may want to do this when
  running Zope under an external server such as a WSGI deployment.

ip-address
  The default IP address on which Zope's various server protocol
  implementations will listen for requests. If this is unset, Zope will listen
  on all IP addresses supported by the machine. This directive can be
  overridden on a per-server basis in the servers section. Defaults to not
  setting an ip-address.

zodb-cache-size
  Set the ZODB cache size, i.e. the number of objects which the ZODB cache
  will try to hold. Defaults to 30000.

zserver-threads
  Specify the number of threads that Zope's ZServer web server will use to
  service requests. The recipes default is 2.

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

Theme resources
---------------

Please refer to `<http://pypi.python.org/pypi/plone.resource>`_ for more
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

Please refer to `<http://pypi.python.org/pypi/RelStorage>`_ for more details
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

event-log-old-files
  Number of previous log files to retain when log rotation is enabled.
  Defaults to 1.

event-log-custom
  A custom section for the eventlog, to be able to use another
  event logger than `logfile`

mailinglogger
  A mailinglogger section added into the event log. Example snippet::

    <mailing-logger>
      level error
      flood-level 10
      smtp-server smtp.mydomain.com
      from logger@mydomain.com
      to errors@mydomain.com
      subject [My domain error] [%(hostname)s] %(line)s
    </mailing-logger>

z2-log
  The filename for the Z2 access log. Defaults to var/log/${partname}-Z2.log.
  Setting this value to 'disable' will make the <logger access> section to be omitted,
  disabling logging access events to a .log file

z2-log-level
  Set the log level for the access log. Level may be any of CRITICAL, ERROR,
  WARN, INFO, DEBUG, or ALL. Defaults to WARN.

access-log-max-size
  Maximum size of access log file. Enables log rotation.

access-log-old-files
  Number of previous log files to retain when log rotation is enabled.
  Defaults to 1.

access-log-custom
  Like `event-log-custom`, a custom section for the access logger, to be able
  to use another event logger than `logfile`.

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
  a disk based cache shared between application threads. It's stored inside
  the directory designated by the `TMP` environment variable.

zeo-client-client
  Set the persistent cache name that is used to construct the cache
  filenames. This enabled the ZEO cache to be persisted. Persistent cache
  files are disabled by default.

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
  Used in the ZEO storage snippets to configure the ZEO var folder.
  Defaults to $INSTANCE_HOME/var.

Advanced options
----------------

before-storage
  Wraps the base storage in a "before storage" which sets it in
  read-only mode from the time given (or "now" for the current time).

  This option is normally used together with demo-storage for a
  normally running site in order for changes to be made to the
  database.

client-home
  Sets the clienthome for the generated instance.
  Defaults to ${buildout:directory}/var/<name of the section>.

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

effective-user
  The name of the effective user for the Zope process. Defaults to not setting
  an effective user.

enable-product-installation
  Enable the persistent product registry by setting this to ``on``. By default
  the registry is turned ``off``. Enabling the registry is deprecated.

ftp-address
  Give a port for the FTP server. This enables the FTP server.

http-force-connection-close
  Set to `on` to enforce Zope to set ``Connection: close header``.
  This is useful if for example a 304 leaves the connection open with
  Varnish in front and Varnish tries to reuse the connection.

http-fast-listen
  Set to `off` to defer opening of the HTTP socket until the end of the Zope
  startup phase. Defaults to on.

icp-address
  Give a port for the ICP server. This enables the ICP server.

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
      zopeskel
    scripts = zopeskel

  In the above example, only zopeskel's scripts will be generated.

var
  Used to configure the base directory for all things going into var.
  Defaults to ${buildout:directory}/var.

webdav-address
  Give a port for the WebDAV server.  This enables the WebDAV server

webdav-force-connection-close
  Valid options are off and on. Defaults to off

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
  the lines of this parameter.

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
  this limit. Default: 8192

  Example::

    http-header-max-length = 16384

Additional Control Script `debug`, `console` and `run` Commands
---------------------------------------------------------------

The extended Zope 2 control script installed by this recipe, usually
`bin/instance` by convention, offers a `debug` command and another
`run` command.  The `debug` command starts an interactive Python
prompt with the Zope 2 application available via the `app` name.
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
create a subprocess to start up Zope 2. This is useful for two
use cases. First, the supervisor program, to supervise long running
processes like a Zope, require the process not to fork away, so that
supervisor can control it.
Second, IDEs like WingIDE and PyCharm support debugging running
processes from within. For this to work, the process should also
not fork away.

Additional control script commands
----------------------------------

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

Reporting bugs or asking questions
----------------------------------

We have a shared bugtracker and help desk on Launchpad:
https://bugs.launchpad.net/collective.buildout/
