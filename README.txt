Introduction
============

This recipe creates and configures a Zope 2 instance in parts. It also
installs a control script, which is like zopectl, in the bin/ directory.
The name of the control script is the the name of the part in buildout.

You can use it with a part like this::

  [instance]
  recipe = plone.recipe.zope2instance
  user = admin:admin
  http-address = 8080
  eggs = ${buildout:eggs} my.package
  products = ${buildout:directory}/products
  zcml = my.package

.. ATTENTION::
   This release is targeted at Zope 2.12+ and Python 2.6. If you are using
   this recipe with earlier versions of Zope or Python, you should use one
   of the releases from the 3.x series.

Options
-------

zope-conf
  A relative or absolute path to a zope.conf file. If this is not given, a
  zope.conf will be generated based on the the options below.

The following options all affect the generated zope.conf:

products
  A list of paths where Zope 2 products are installed. The first path takes
  precedence in case the same product is found in more than one directory.

site-zcml
  If you want a custom site.zcml file, put its content here. If this option is
  used the zcml and zcml-additional options are ignored.

zcml
  Install ZCML slugs for the packages listed, separated by whitespace. You
  can specify the type of slug by appending '-' and the type of slug you want
  to create.  The valid types are configure, overrides and meta. Some
  examples: my.package-overrides my.package-meta

zcml-additional
  Extra ZCML statements that should be included in the generated site.zcml
  file.

extra-paths
  A list of paths where additional python packages are installed. The paths
  are searched in the given order after all egg and products paths.

default-zpublisher-encoding
  This controls what character set is used to encode unicode data that reaches
  ZPublisher without any other specified encoding. This defaults to 'utf-8'.

debug-mode
  Set to 'on' to turn on debug mode in Zope. Defaults to 'off'.

verbose-security
  Set to 'on' to turn on verbose security (and switch to the Python security
  implementation). Defaults to 'off' (and the C security implementation).

effective-user
  The name of the effective user for the Zope process. Defaults to not setting
  an effective user.

ip-address
  The default IP address on which Zope's various server protocol
  implementations will listen for requests. If this is unset, Zope will listen
  on all IP addresses supported by the machine. This directive can be
  overridden on a per-server basis in the servers section. Defaults to not
  setting an ip-address.

port-base
  Offset applied to the port numbers used for ZServer configurations. For
  example, if the http-server port is 8080 and the port-base is 1000, the HTTP
  server will listen on port 9080. This makes it easy to change the complete
  set of ports used by a Zope server process. Zope defaults to 0.

http-address
  Give a port for the HTTP server. Defaults to 8080.

http-fast-listen
  Set to off to defer opening of the HTTP socket until the end of the Zope
  startup phase. Defaults to on. Note: This option requires Zope >= 2.11.

ftp-address
  Give a port for the FTP server. This enables the FTP server.

webdav-address
  Give a port for the WebDAV server.  This enables the WebDAV server

webdav-force-connection-close
  Valid options are off and on. Defaults to off

icp-address
  Give a port for the ICP server. This enables the ICP server.

client-home
  Sets the clienthome for the generated instance.
  Defaults to ${buildout:directory}/var/<name of the section>.

var
  Used to configure the base directory for all things going into var.
  Defaults to ${buildout:directory}/var.

event-log
  The filename of the event log. Defaults to var/log/${partname}.log

event-log-custom
  A custom section for the eventlog, to be able to use another
  event logger than `logfile`

event-log-level
  Set the level of the console output for the event log. Level may be any of
  CRITICAL, ERROR, WARN, INFO, DEBUG, or ALL. Defaults to INFO.

z2-log
  The filename for the Z2 access log. Defaults to var/log/${partname}-Z2.log.

z2-log-level
  Set the log level for the access log. Level may be any of CRITICAL, ERROR,
  WARN, INFO, DEBUG, or ALL. Defaults to WARN.

access-log-custom
  Like `event-log-custom`, a custom section for the access logger, to be able
  to use another event logger than `logfile`.

file-storage
  The filename where the ZODB data file will be stored.
  Defaults to var/filestorage/Data.fs.

demo-storage
  If 'on' it enables the demostorage. It is not compatible with blob-storage
  and rel-storage.

blob-storage
  The name of the directory where the ZODB blob data will be stored.

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

zeo-client
  Set to 'on' to make this instance a ZEO client. In this case, setting the
  zeo-address option is required, and the file-storage option has no effect.
  To set up a ZEO server, you can use the plone.recipe.zope2zeoserver recipe.
  Defaults to 'off'.

shared-blob
  If 'zeo-client' is set to 'on' and 'blob-storage' is set to a directory that
  is shared between this instance and the ZEO server (as configured by the
  'blob-dir' setting on zeo.conf, then setting 'shared-blob' to 'on' causes
  this instance not to stream the blob file through the ZEO connection, but
  just to send the information of the file location to the ZEO server.

zeo-address
  Set the address of the ZEO server. Defaults to 8100.

zeo-client-name
  Set the name of the ZEO client. Defaults to the name of the part. If a false
  value is provided no zeo-client-name will be set.

zeo-client-cache-size
  Set the size of the ZEO client cache. Defaults to '30MB'.

zeo-client-client
  Set the persistent cache name that is used to construct the cache
  filenames. Persistent cache files are disabled by default.

zeo-storage
  Set the storage number of the ZEO storage. Defaults to '1'.

zeo-var
  Used in the zeo storage snippets to configure the zeo var folder.
  Defaults to $INSTANCE_HOME/var.

zeo-username
  Enable ZEO authentication and use the given username when accessing the
  ZEO server. It is obligatory to also specify a zeo-password.

zeo-password
  Password to use when connecting to a ZEO server with authentication
  enabled.

zeo-realm
  Authentication realm to use when authentication with a ZEO server. Defaults
  to 'ZEO'.

zodb-cache-size
  Set the ZODB cache size, i.e. the number of objects which the ZODB cache
  will try to hold. Defaults to 5000.

zodb-cache-size-bytes
  Set the ZODB cache sizes in bytes. Requires ZODB 3.9 or later.

zserver-threads
  Specify the number of threads that Zope's ZServer web server will use to
  service requests. You shouldn't change this unless you know what you are
  doing. The recipes default is 2.

python-check-interval
  An integer telling the Python interpreter to check for asynchronous events
  every number of instructions. This affects how often thread switches occur.

enable-product-installation
  Enable the persistent product registry by setting this to ``on``. By default
  the registry is turned ``off``.

zodb-temporary-storage
  If given Zope's default temporary storage definition will be replaced by
  the lines of this parameter.

environment-vars
  Define arbitrary key-value pairs for use as environment variables during
  Zope's run cycle.

  Example::

    environment-vars =
      TZ US/Eastern
      TMP /var/tmp
      DISABLE_PTS True

zope-conf-additional
  Give additional lines to zope.conf. Make sure you indent any lines after
  the one with the parameter.

  Example::

    zope-conf-additional =
      locale fr_FR
      http-realm Slipknot

relative-paths
  Set this to `true` to make the generated scripts use relative
  paths. You can also enable this in the `[buildout]` section.

Additional control script commands
----------------------------------

Third-party packages may add additional commands to the control script by
installing a 'plone.recipe.zope2instance.ctl' entry point. For example,
an egg called mypackage could include a module called mypackage with the
following custom command::

    def foo(self, *args)
        """Help message here"""
        print 'foo'

It would then install the foo method as a command for the control script using
the following entry point configuration in setup.py::

    entry_points="""
    [plone.recipe.zope2instance.ctl]
    foo = mypackage:foo
    """

This would allow invoking the foo method by running `bin/instance foo`
(assuming the instance control script was installed by a buildout part
called `instance`.)  The entry point is invoked with the following
parameters:

  self
    An instance of plone.recipe.zope2instance.ctl.AdjustedZopeCmd.
  args
    Any additional arguments that were passed on the command line.

Reporting bugs or asking questions
----------------------------------

We have a shared bugtracker and help desk on Launchpad:
https://bugs.launchpad.net/collective.buildout/
