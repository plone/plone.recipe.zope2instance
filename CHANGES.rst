Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

8.0.1 (2025-04-04)
------------------

Bug fixes:


- Check for presence of Products.CMFPlone with multiple keys.
  This is needed, depending on the used `zc.buildout` and `setuptools` versions.
  [maurits] (#205)


8.0.0 (2025-03-13)
------------------

Breaking changes:


- Drop support for Python 3.8. (#202)


New features:


- support for Zope option `enable-xmlrpc` (#200)
- Add official support for Python 3.13. (#202)


7.1.2 (2024-11-25)
------------------

Documentation:


- Remove obsolete attention admonition. The `master` branch supports Plone 6.x. (#199)


7.1.1 (2024-09-24)
------------------

Bug fixes:


- Fix wsgi_ini_template creation when recipe is called multiple times.
  [petschki] (#197)
- Installing the recipe twice should not break; remove use of `global`
  [gotcha] (#198)


7.1.0 (2024-09-19)
------------------

New features:


- Specify a standalone logging.ini configuration using the wsgi-logging-ini-template option in buildout.
  The log configuration will be injected into wsgi.ini keeping all other default wsgi config.
  The wsgi-logging-ini-template option cannot be used together with the wsgi-ini-template. @Sakoes (#59)


7.0.0 (2024-08-01)
------------------

Breaking changes:


- Drop support for Python 3.7 and lower, Zope 4, Plone 5.2.
  [maurits] (#194)


6.13.0 (2024-04-23)
-------------------

New features:


- Add support for setting max_value_length in Sentry init.
  When you use this option, you should use `sentry-sdk` 1.29.0 or higher.
  [gyst] (#193)


Tests


- Update tox to support python 3.10 and 3.11. (#193)


6.12.2 (2023-09-26)
-------------------

New features:


- Add ``dos_protection`` config.
  With Zope 5.8.4+ you may get ``zExceptions.BadRequest: data exceeds memory limit`` when uploading an image or file of more than 1 MB.
  To increase this limit, you can add this in your instance recipe, and choose your own limit::

    zope-conf-additional =
      <dos_protection>
        form-memory-limit 4MB
      </dos_protection>

  [@mamico] (#191)


6.12.1 (2023-09-08)
-------------------

Documentation:


- Update README: for ``RotatingFileHandler`` ``maxCount`` is not a valid keyword argument.
  Use ``backupCount``.
  [gforcada] (#190)


6.12.0 (2023-01-31)
-------------------

New features:


- Add new option `asyncore_use_poll` to waitress config file.
  [petschki] (#189)


6.11.0 (2022-03-23)
-------------------

New features:


- By default, do not create a tempstorage on Plone 6.
  See `issue 180 <https://github.com/plone/plone.recipe.zope2instance/issues/180>`_.
  [maurits] (#180)


6.10.2 (2021-10-07)
-------------------

Bug fixes:


- Fix ``python-dotenv`` dependency for Python 2 compatibility. [dataflake] (#181)


6.10.1 (2021-09-01)
-------------------

Bug fixes:


- Fix resource warning in tests.  [icemac] (#176)


6.10.0 (2021-05-11)
-------------------

New features:


- Allow to customize the WSGI pipeline [ale-rt, jensens] (#116)
- Add repoze.profile profiling middleware support [jensens] (#129)


Bug fixes:


- Enable both weekly and manual builds for GitHub Actions [jugmac00] (#169)
- Fix unsupported syntax in the requirements files which prevented to evaluate
  the specified constraints during test runs [jugmac00]. (#171)
- Applied code style black and isort with Plone/black rules, includes tox/GH-Actions  [jensens] (#175)


6.9.0 (2021-03-22)
------------------

New features:


- Make any ctl script python-env aware
  [sneridagh] (#162)
- Added support for Python 3.9 and restored support for Python 3.5 (needed for Zope 4)
  [dataflake] (#164)


Bug fixes:


- Fixed ``$PYTHONSTARTUP`` file support for the ``debug`` command under Python 3
  [dataflake] (#167)


6.8.3 (2021-02-17)
------------------

Bug fixes:


- Fix windows `wsgi.ini` to have a configurable listen address.
  Added missing WSGI config options for windows.
  [jensens] (#161)


6.8.2 (2021-02-16)
------------------

Bug fixes:


- Restored ability to use own explicit version of zodb-temporary-storage.
  [maurits] (#93)


6.8.1 (2020-10-30)
------------------

Bug fixes:


- Properly disable access-log for WSGI.
  [tschorr] (#159)


6.8.0 (2020-09-26)
------------------

New features:


- Added option ``clear-untrusted-proxy-headers``, with default false.
  See waitress documentation on `clear_untrusted_proxy_headers <https://waitress.readthedocs.io/en/latest/arguments.html?highlight=clear_untrusted_proxy_headers>`_.
  Fixes a `deprecation warning <https://github.com/plone/plone.recipe.zope2instance/issues/142>`_.
  [maurits] (#142)
- Added option ``max-request-body-size``, with default 1073741824.
  See waitress documentation on `max_request_body_size <https://waitress.readthedocs.io/en/latest/arguments.html?highlight=max_request_body_size>`_.
  [mpeeters] (#155)


Bug fixes:


- Add GitHub Actions to project.
  Run tests there in a matrix against Zope 4 and Zope 5, Windows and Linux, Python 27, 3.6, 3.7 and 3.8.
  Testing Python 2.7 on Windows is skipped.
  Refactor tox test setup slightly, do not use tox on GitHub.
  Split up tests in smaller easier to maintain files.
  Fix tests to run on Windows without tocuhing the recipe code (the Windows code is not perfect right now, but it test are reflecting current state).
  This primary includes respecting path-handling (backslash vs slash), conditional instance generation and differences in wsgi configurations.
  Also resolves "unclosed files" warnings.
  Reflect Zope 5 and so Plone 6.0 support in trove classifiers.
  [jensens] (#150)


6.7.5 (2020-08-16)
------------------

Bug fixes:


- Generate working ``wsgi.ini`` on windows.
  Do not generate instance script.
  Need to use ``.\bin\runwsgi.exe -dv .\parts\etc\wsgi.ini`` on windows to start.
  [jensens] (#151)


6.7.4 (2020-08-14)
------------------

Bug fixes:


- Fix "SyntaxError" on windows: Generate raw strings in order to allow backslashes in log file paths.
  [jensens] (#145)
- Fixed an issue that prevented the instance to start
  when http-address has multiple entries and http-fast-listen is on
  [ale-rt] (#146)
- WSGI instances do not fail to start when http-address is equal to a list of ports [ale-rt] (#148)


6.7.3 (2020-07-30)
------------------

Bug fixes:


- Set the default for the http-fast-listen to on to match the documentation [ale-rt] (#71)


6.7.2 (2020-06-28)
------------------

Bug fixes:


- Fix flake8 and fix inserting ``CHAMELEON_CACHE`` in some cases.  [ale-rt] (#139)


6.7.1 (2020-04-21)
------------------

Bug fixes:


- Minor packaging updates. (#1)


6.7.0 (2020-03-09)
------------------

New features:


- added relstorage w/ sqlite support
  [mamico] (#132)


6.6.0 (2020-02-18)
------------------

New features:


- Support for Zope options ``webdav-source-port`` and ``enable-ms-public-header``.
  [dataflake] (#134)


6.5.1 (2019-11-25)
------------------

Bug fixes:


- for initialization option, string format works for instance console script not for the others
  [mamico] (#130)


6.5.0 (2019-10-12)
------------------

New features:


- added `wsgi-ini-template` option for specifying a custom template for the generation of the `wsgi.ini` configuration file [ajung] (119-1)
- advanced WSGI logging configuration options for specifying arbitrary logging handlers for event and access log [ajung] (119-2)
- added documentation and examples for advanced WSGI logger configuration [ajung] (119-3)


Bug fixes:


- Add documentation for `threads` option. (#126)
- Fix documentation for http-address option. (#127)


6.4.0 (2019-08-29)
------------------

New features:


- Add Sentry support by adding a new filter to the WSGI pipeline. (#124)


Bug fixes:


- Fixed a deprecation warning when importing ``makerequest`` from ``Testing.ZopeTestCase.utils``.
  This also fixes a side effect which can bite you if you rely on the ``ZOPETESTCASE`` environment variable, only being set to ``1`` during test runs. (#122)


6.3.0 (2019-07-06)
------------------

New features:


- Enable CHAMELEON_CACHE by default. See https://github.com/plone/Products.CMFPlone/issues/2898
  [pbauer] (#118)


6.2.2 (2019-06-19)
------------------

Bug fixes:


- Fix startup issues by adding support for new Zope configuration keys
  ``zmi-bookmarkable-urls`` and ``pid-filename`` (#112)


6.2.1 (2019-05-10)
------------------

Bug fixes:


- Clarify documentation for the `scripts` option (#29)
- Fix handling of ZEO client persistent cache and storage settings (#30)
- Try to look up a suitable log file for the ``logtail`` verb (#85)
- Fixed invalid import path for DeprecationWarning for ``warnfilter`` (#105)
- Document where ``restart`` can break in the project README (#107)
- Prevent constant `waitress.queue` log messages on the console and just send
  them to the event log. (#110)


6.2.0 (2019-05-04)
------------------

New features:


- Add support for the new ``debug-exceptions`` flag in Zope (#100)


6.1.5 (2019-04-24)
------------------

New features:


- Add the ability to specify a custom WSGI configuration file (#90)


Bug fixes:


- Enable socket reuse to prevent startup errors when running in the foreground (#86)
- Add ability to turn off ``zodb-temporary-storage`` to prevent Zope 4 breakage (#87)
- Fix WSGI access log formatting configuration (#88)
- Fix ZServer instance creation with better WSGI flag checking (#95)


6.1.4 (2019-03-21)
------------------

Bug fixes:


- Fix zdaemon socket location when it's not passed on the command line (`#79 <https://github.com/plone/plone.recipe.zope2instance/pull/79>`_). [tschorr] (#79)
- remove unknown key `effective-user` for wsgi configuration (#80)
  [petschki] (#80)
- Use built-in function next [erral] (#82)


6.1.4 (unreleased)
------------------

Bug fixes:

- restore http-fast-listen for waitress (`#71 <https://github.com/plone/plone.recipe.zope2instance/issues/71>`_)
  [tschorr]


6.1.3 (2019-03-04)
------------------

Bug fixes:


- Restore log files for waitress. [tschorr] (#76)


6.1.2 (2019-03-03)
------------------

Breaking changes:


- Change the default to enable wsgi unless running Python 2 and setting
  wsgi=off. See https://github.com/plone/Products.CMFPlone/issues/2763 [pbauer]
  (#73)


6.1.1 (2019-02-08)
------------------

Bug fixes:

- log level for Plone WSGI logger changed to INFO making the logging less
  verbose [ajung] (#66)
- Improve debugging of run scripts by providing the source code for the
  debugger. [icemac] (#68)
- Use correct debug switch for WSGI. (`Products.CMFPlone #2719
  <https://github.com/plone/Products.CMFPlone/issues/2719>`_) Display warnings
  in debug mode with WSGI (override with PYTHONWARNINGS). (`Products.CMFPlone
  #2724 <https://github.com/plone/Products.CMFPlone/issues/2724>`_) [tschorr]
  (#69)
- Fix Flake8 issues in the code. [icemac] (#72)


6.1.0 (2018-12-28)
------------------

New features:

- Add new option 'threads' used to specify the number of workers for both
  waitress + ZServer, and a deprecation warning for 'zserver-threads'.
  [tschorr]

- Add support for Python 3.7 while dropping official support for Python 3.5.
  (`#60 <https://github.com/plone/plone.recipe.zope2instance/issues/60>`_)

Bug fixes:

- Make comments in zcml values work, even if not starting at the beginning of the line;
  before, we had a confusing error message. Fixes #46
  [tobiasherp]

- Fixed serving Plone with WSGI when ZServer is also installed on Python 2.
  [davisagli]

- Remove `path` option from zope.conf generated when using WSGI as it is no longer understood.
  [icemac]

- Remove `deprecation-warnings` option from zope.conf generated
  when using WSGI as it is no longer understood.
  [davisagli]


6.0.0 (2018-11-08)
------------------

Breaking changes:

- For WSGI-based instances, generate a zdaemon-based instance script
  that works similarly to ZServer-based instances, instead of a
  script that only handles running the WSGI server.
  [davisagli]


5.0.1 (2018-11-04)
------------------

Bug fixes:

- Super user password created on Python 3 can now be read by Zope.
- Fix WSGI initialization
  [tschorr]
- Move Recipe from __init__.py to a new module to get rid of the dependency on
  zc.recipe.egg in control scripts
  [tschorr]
- Make use of changes to Zope WSGI logging
  (`#280 <https://github.com/zopefoundation/Zope/pull/280>`_,
  `#276 <https://github.com/zopefoundation/Zope/pull/276>`_),
  use Zope2 WSGI startup code.
  [tschorr]
- Fix the tests on Python 3 when running via tox or TravisCI.
  [icemac]


5.0.0 (2018-01-27)
------------------

Breaking changes:

- Require at least ZODB 5 and Zope 4.0b1.

- Drop support for Plone 4.3, 5.0, and 5.1.

New features:

- Add wsgi support
  [tschorr]

- Add support for Python 3.5 and 3.6.

Bug fixes:

- Python 3 compatibility with sixer
  [ale-rt]

- Fix import. zopectl moved to ZServer
  [pbauer]


4.3 (2017-06-28)
----------------

New features:

- Added ``storage-wrapper`` option to wrap storage configuration.
  [davisagli]


4.2.22 (2016-10-05)
-------------------

Bug fixes:

- Add coding headers on python files.
  [gforcada]

4.2.21 (2016-05-26)
-------------------

Fixes:

- Fix #23: "TypeError: <lambda>() takes no arguments (1 given)" on ./bin/instance start
  [jensens]


4.2.20 (2016-03-29)
-------------------

Fixes:

- Revert changes made on previous release.
  The way zopectl and this recipe handle commands
  is totally different.
  [gforcada]


4.2.19 (2016-02-15)
-------------------

New:

- Handle commands registered for zopectl as well.
  Up to now they were handled but not displayed at all
  (i.e. in help and descriptions).
  https://github.com/plone/plone.recipe.zope2instance/issues/18
  [gforcada]


4.2.18 (2015-07-27)
-------------------

- Allow to disable logs.  Set ``z2-log`` to the value ``disable`` to
  disable the Z2 access log.  Set ``event-log`` to the value
  ``disable`` to disable the event log.
  [frapell]


4.2.17 (2015-04-29)
-------------------

- Added `zope-conf-imports` option to easily import ZConfig components
  within zope.conf using %import syntax.
  [avoinea]


4.2.16 (2014-11-01)
-------------------

- If ''demo-file-storage' is set, but 'demo-storage' is off, do not
  raise an exception
  [frapell]

- Add documentation for console command, for supervisor and IDE
  debugging
  [do3cc]


4.2.15 (2014-09-07)
-------------------

- Always wrap contents of zcml-additional with a <configure /> node.
  This makes it possible to use += assignments with zcml-additional.
  [lgraf]
- Add support for multiple zeo servers
  [ivant]


4.2.14 (2014-03-02)
-------------------

- Link to zope.conf is now relativitize if option relative-paths is true.
  [bsuttor]
- Added ability to set ``initialization`` to configure Python
  code to run on instance start up.
  [davidjb]
- added support for http-header-max-length
  [alecghica]


4.2.13 (2013-07-28)
-------------------

- adding support for zopectl umask
  [hman]


4.2.12 (2013-06-04)
-------------------

- be able to set zeo client as read only from buildout configuration
  [vangheem]


4.2.11 (2013-05-23)
-------------------

- When creating the blobstorage dir, make it only readable for the
  current user, otherwise you get a ZODB warning on startup.  This
  uses code from the ZODB, which does the same when Zope starts up and
  the blobstorage directory does not exist yet.
  [maurits]

- Fixed check for empty custom_access_event_log and custom_event_log.
  [alecghica]


4.2.10 (2013-03-05)
-------------------

- Recipe would fail if eggs are stored in readonly cache. Don't copy
  permissions from the egg.
  [garbas]


4.2.9 (2013-02-10)
------------------

- Add trove classifiers to note Python version compatibility.
  [hannosch]


4.2.8 (2013-01-17)
------------------

- Pass python flags to Zope interpreter as well. This prevents the debug
  command from exiting directly.
  [wichert]


4.2.7 (2013-01-13)
------------------

- Load PYTHONSTARTUP if defined when running the debug command.
  [mj]


4.2.6 (2012-12-09)
------------------

- Use interpreter script instead of setting PYTHONPATH.  Fixes Windows
  "the environment variable is longer than 32767 bytes" error.
  [rossp]

- Make the zope.conf http-server optional by setting http-address to
  an empty string.  Useful for configurations used under an external
  server such as a WSGI deployment.
  [rossp]

4.2.5 (2012-09-20)
------------------

- Added event and access log rotation capability.
  [sureshvv]

4.2.4 (2012-08-29)
------------------

- Expose 'drop-cache-rather-verify' ZEO client option which indicates that
  the cache should be dropped rather than verified when the verification
  optimization is not available (e.g. when the ZEO server restarted).
  [runyaga]

- Strip all empty lines out of zeo.conf to provide more compact view.
  [runyaga]

4.2.3 (2012-08-04)
------------------

- Fix zcml load order of the optional locales directory. Translation overrides
  need to be loaded first.
  [sunew]

4.2.2 (2012-07-02)
------------------

- Changed client connection cache defaults. We specify a cache size of 30000
  instead of 10000.
  [hvelarde]

- Add new `locales` option for specifying a locales directory with
  extra or different translations.
  [maurits]

4.2.1 (2012-04-15)
------------------

- Add control script `debug` and `run` support to set up a REQUEST,
  log in the AccessControl.SpecialUsers.system user, and traverse to
  an object, such as a CMF portal.
  [rpatterson]

4.2 (2011-11-24)
----------------

- Add support for a changes storage for demo storage (in addition to
  the base storage). Local file and blob storage is supported.
  [malthe]

- Add support for before storage (via the ``zc.beforestorage`` package).
  [malthe]

- Make script suppression optional (via empty `scripts` parameter). Otherwise,
  scripts for packages listed in `eggs` parameter will be generated.
  [aclark]

- Support all RelStorage options, even future options. Used a simple pattern
  to recognize where options should be placed: any option name containing a
  dash is a generic option; the rest (except "name") are database-specific.
  [hathawsh]

4.1.9 - 2011-08-11
------------------

- No longer rely on `softwarehome` in startup script.
  [hannosch]

4.1.8 - 2011-07-17
------------------

- Add preliminary support for Zope 4.0, by re-using the skeleton for 2.13.
  [hannosch]

- Added `zeo-client-blob-cache-size` and `zeo-client-blob-cache-size-check`
  options to control maximum size of blob cache, and when to check the size,
  when using ClientStorage without shared blobs.
  [davidjb]

- If a resource directory is specified using `resources`, create it if it does
  not yet exist.
  [davisagli]

- Support the new create-schema option introduced in RelStorage 1.5.0b2.
  [mj]

4.1.7 - 2011-06-07
------------------

- Renamed the optional ``998-resources.zcml`` (introduced in 4.1.6) to
  ``998-resources-configure.zcml``, otherwise it does not get loaded
  in the standard ``site.zcml``.
  [maurits]


4.1.6 - 2011-06-01
------------------

- Add new `resources` option for specifying a plone.resource central resource
  directory.
  [elro]

4.1.5 - 2011-02-17
------------------

- Respect new `include-site-packages` buildout option introduced in buildout
  1.5. Closes https://bugs.launchpad.net/bugs/716360.
  [yuppie, hannosch]

- Added option `import-directory` to point to custom import folder.
  [garbas]

4.1.4 - 2011-01-01
------------------

- Removed `zeo-client-name` option. The option had no effect since ZODB 3.2
  and was removed in Zope 2.13. This closes
  https://bugs.launchpad.net/bugs/694920.
  [hannosch]

4.1.3 - 2010-12-20
------------------

- Added option http-force-connection-close which was only present in comment.
  [tesdal]

4.1.2 - 2010-12-05
------------------

- Fixed error introduced in 4.1.1.
  [hannosch]

4.1.1 - 2010-12-05
------------------

- Disambiguate the `blob-storage` option if `shared-blob` isn't used. In this
  case we use `var/blobcache` as a default location, so we don't accidentally
  overwrite the real blob data with a blob zeocache. Refs
  https://bugs.launchpad.net/bugs/645904.
  [hannosch]

4.1 - 2010-12-04
----------------

- Give the `readme` an overhaul, group options into sections and mention the
  most commonly used ones at the top.
  [hannosch]

- Add some flexibility to `site.zcml` creation. Thanks to Wolfgang Schnerring
  for the patch. This closes
  https://bugs.launchpad.net/collective.buildout/+bug/335311.
  [hannosch]

- Raise an exception if both ZEO and RelStorage are configured at the same
  time. This closes https://bugs.launchpad.net/collective.buildout/+bug/645100.
  [hannosch]

- Added support for zc.buildout 1.5, while retaining support for 1.4. Thanks
  to Jeff Rush for the patch. This closes
  https://bugs.launchpad.net/collective.buildout/+bug/683584.
  [hannosch]

4.0.5 - 2010-10-22
------------------

- Added support for specifying the new RelStorage options shared-blob-dir,
  blob-cache-size, blob-cache-size-check, and blob-chunk-size.
  [hathawsh]

4.0.4 - 2010-09-09
------------------

- Add friendly error message if non-admin tries
  "instance install|start|restart|stop|remove".
  [kleist]

- Exit with the return code of the executed do_* method. This closes #10906
  (clicking "Restart" in ZMI control panel caused shutdown).
  [kleist]

- Implemented the "restart" command for "bin/instance.exe".
  [kleist]

4.0.3 - 2010-08-20
------------------

- Setuptools / Subversion ignores empty directories and doesn't include them
  into the source distribution. Added readme files to the `bin` and `var`
  directories inside the skeleton. This lets persistent ZEO caches work again,
  which want to put their files into the `var` directory.
  [hannosch]

4.0.2 - 2010-08-04
------------------

- Rewritten major parts of commands specific for the Windows Service, inspired
  by "collective.buildout.cluster.base.ClusterBase" as used by the Windows
  installer. Closes http://dev.plone.org/plone/ticket/10860.
  [kleist]

4.0.1 - 2010-07-30
------------------

- Use pid file to check for running application, instead of service status.
  [sidnei]

4.0.0 - 2010-07-21
------------------

- "console" mode on Windows no longer returns immediately, thus makes it
  usable by the Windows Service.
  [kleist]

- Made tests compatible with Windows.
  [hannosch]

- Added support for specifying new RelStorage options cache-local-mb,
  cache-delta-size-limit, commit-lock-timeout and commit-lock-id.
  [hannosch]

4.0b2 - 2010-06-23
------------------

- Added a new dependency on ``mailinglogger`` and expose it as a convenient
  new option.
  [hannosch]

- Removed testing dependency on ``zope.testing`` and refactored test setup.
  [hannosch]

4.0b1 - 2010-04-04
------------------

- The recipe could sometimes fail to build twice if no zcml option was given.
  This closes http://dev.plone.org/plone/ticket/10296.
  [hannosch]

4.0a4 - 2010-02-04
------------------

- Removed commented out options from the http-server section.
  [hannosch]

- Added new ``enable-product-installation`` option and let it default to off.
  [hannosch]

4.0a3 - 2010-01-24
------------------

- Tried to restore the Windows service functionality, getting closer but not
  there yet all the way.
  [hannosch]

- Use the same quoting approach for the console as for fg command on Windows.
  [hannosch]

- Don't call zopectl.quote_command(), since the added outer double quotes caused
  subprocess.call() to fail with "WindowsError: [Error 87] The parameter is
  incorrect". Instead, hand roll the quoting (save outer quotes).
  [kleist]

- Un-hardcoded ':' as path separator, caused "ImportError: No module named
  Zope2.Startup" on Windows. See http://dev.plone.org/plone/ticket/9991.
  [kleist]

- Removed the import directory from the skeleton. You can place import files
  into the import directory in the client home in new Zope 2 versions.
  [hannosch, davisagli]

- Make it possible to omit the user option, in which case buildout will ask
  for a user and password, when a new instance is created.
  [hannosch]

- Use our own make instance script and skeletons, only providing what we
  really need anymore.
  [hannosch]

- Merge the two ZopeCmd classes into one. We don't rely or generate the runzope
  script or anything inside parts/instance/bin anymore.
  [hannosch]

- By default create a blob-storage in ``var/blobstorage``.
  [hannosch]

- Removed the ``no-shell`` option and made it the default for running the
  process. This also removes the need for the ``runzope`` script.
  [hannosch]

- This version can no longer be used to install a non-eggified Zope2. The
  ``zope2-location`` option was removed.
  [hannosch]

4.0a2 - 2009-12-02
------------------

- Make it possible for third-party packages to add additional commands to the
  control script by supplying a 'plone.recipe.zope2instance.ctl' entry point.
  [davisagli]

4.0a1 - 2009-11-14
------------------

- Removed the test command support from the control script which lets us
  remove quite a bit of hackery. Added a note about using ``bin/test`` instead.
  [hannosch]

- Added an explicit `python-check-interval` option and change its default to
  `1000` instead of Python's own default of `100`.
  [hannosch]

- Changed default `zserver-threads` to two instead of four.
  [hannosch]

- Changed client connection cache defaults. We specify a cache size of 10000
  instead of 5000. Also changed ZEO client cache to 128MB instead of 30MB.
  [hannosch]

- If we are used in an environment with Zope2 as an egg, we make sure to
  install the mkzopeinstance and runzope scripts we depend on ourselves.
  This is done even if they already exist, since the eggs may have changed.
  [hannosch, davisagli]

- Added Zope2 egg to the list of dependencies of this recipe. This can cause
  trouble for Zope versions before Zope 2.12 or Plone before 4.0.
  [hannosch]

- Added the cache-prefix option for RelStorage.

3.6 (2009-10-11)
----------------

- Expanded the RelStorage options, including keep-history and replica-conf.
  [hathawsh]

3.5 (2009-09-05)
----------------

- Added support for relative-paths in the script generation.
  [jvloothuis]

- When `zope-conf` is set the config file will be directly loaded from that
  location (it previously created a stub zope.conf which included it).
  [jvloothuis]

- Added an option to avoid using the normal shell scripts for starting Zope.
  This makes it possible to avoid the hard-coded paths in these scripts.
  [jvloothuis]

- Allow the blob-dir parameter in RelStorage configurations.
  [hathawsh]

3.4 (2009-08-12)
----------------

- Support in line with fix for LP#407916.
  [gotcha]

- Changed the 'mkzopeinstance' call respect the 'bin-directory' option.
  [esteele]

- Removed the `zope2-egg` option and the simple startup script from the recipe.
  We assume that we have an egg distribution if `zope2-location` is not set.
  [hannosch]

- Merged the `davisagli-eggified-zope` branch into the trunk.
  [hannosch]

- Add a new icp-address option. This is useful for environments where
  e.g. squid is used to front a Zope/ZEO cluster. See
  http://www.zope.org/Members/htrd/icp/intro
  [neaj]

3.3 - 2009-07-07
----------------

- Add handling for RelStorage options.
  [elro]

- Reinstall scripts on update which appears to be good recipe practice.
  [stefan]

3.2 - 2009-04-02
----------------

- Add a new zcml-additional option. This is useful for environments where
  non-code configuration (such as database connection details for
  ore.contentmirror) are managed through zcml.
  [wichert]

3.1 (2009-03-15)
----------------

- The 2.9 fix for spaces caused a problem using debug (bug 337740)
  due to the way do_debug passed the "-i" command line argument
  to get_startup_cmd.
  [smcmahon]

3.0 (2009-02-27)
----------------

- The 2.9 fix for the instance run command was itself broken and
  would fail on anything except Windows.
  [smcmahon]

- Changed the `zope2-egg` option to omit any kind of instance creation for
  now. The mkzopeinstance script relies on being able to import Zope2, which
  is not available when buildout runs.
  [hannosch]

2.9 (2009-02-26)
----------------

- The instance run command was vulnerable to spaces in pathnames, and
  needed some extra quoting for win32.
  [smcmahon]

- Check for existence of windows scripts before patching them. Some
  Linux distributions of Zope2 don't have these files.
  [smcmahon]

- Delegate commands to ``win32serviceutil.HandleCommand()`` on win32,
  instead of starting the interpreter through ``os.system()``. Should
  shave off a couple seconds from overall time taken to process those
  commands.
  [sidnei]

- Compute ``serviceClassString`` ourselves, since we are calling this
  as a module and not directly as ``__main__``, otherwise the service
  won't be installed correctly.
  [sidnei]

2.8 (2008-12-05)
----------------

- Add more tests for ZEO client with blob and demo storages.
  Still no test on 'shared-blob-dir' option.
  [encolpe]

- Always use 'r'-style strings for passing script and configuration
  filenames (eg: on 'instance run <script>').
  [sidnei]

- Add a demo-storage option and tests.
  [encolpe]

- Add a first test for blob-storage.
  [encolpe]

2.7 (2008-11-18)
----------------

- Added a `zope2-egg` option and an accompanying simple startup script for
  use with an eggified Zope2.
  [hannosch]

- Do not fail with a Zope2 egg checkout.
  [hannosch]

- Normalize first argument to os.spawnl. It can get really upset
  otherwise (dll import failure on a relocatable python install).
  [sidnei]

- Use same quoting as on 'do_foreground' for servicescript
  usage. Fixes problems with installing the buildout-based Plone
  installer for Windows on a path with spaces.
  [sidnei]

- Ensure that do_foreground leaves self.options.program arguments as it
  found them.  This makes it possible to use 'fg' and 'debug' more than
  once within the same control session.
  [klm]

2.6 (2008-10-22)
----------------

- Normalize, absolutize and lowercase-ize (is that a word?) paths
  before comparing, to avoid problems with relative filenames and
  different drive letter case on Windows.
  [sidnei]

2.5 (2008-09-22)
----------------

- Add support for zodb-cache-size-bytes from ZODB 3.9 and later.
  [wichert]


2.4 (2008-07-15)
----------------

- Introduced zope.conf variables "INSTANCEHOME" and "CLIENTHOME".
  Its very very helpful in cluster setups with zope-conf-additional
  sections (buildout lacks to reference the current section).
  [jensens]

- Made test command compatible with zope.testing 3.6.
  [hannosch]

2.3.1 (2008-06-10)
------------------

- No code changes. Released to fix the 2.3 release which put .egg files in
  the wild.
  [hannosch]

2.3 (2008-06-06)
----------------

- Need to actually pass in deprecation-warnings, otherwise we get a
  KeyError.
  [sidnei]

- Fix another place where the directory name needed to be escaped to
  avoid problems with spaces.
  [sidnei]

- Don't try to delete location if it does not exist.
  [sidnei]

2.2 (2008-06-06)
----------------

- Added `deprecation-warnings` option that allows turning the option
  to disable deprecation warnings on or off. You can provide the value
  `error` to it, and every deprecation warning will be turned into an
  exception.
  [sidnei]

- Fix copy and paste error that caused a failure on changing
  runzope.bat to call servicewrapper.py.
  [sidnei]

- Escape 'executable' argument before passing it to os.spawnl, in
  order to make it work on Windows when the executable name has spaces
  on it.
  [sidnei]

- Added `http-fast-listen` option. Use of this option requires Zope >= 2.11.
  [stefan]

2.1 (2008-06-05)
----------------

- Fixed a test problem on Windows, where explicit closing of files is required.
  [hannosch]

- Call `servicewrapper.py` from `runzope.bat` instead of setting
  `PYTHONPATH` and calling `Zope2/Startup/run.py`. That way we set
  sys.path from inside Python code and avoid exceeding the maximum
  environment variable limit.
  [sidnei]

- Allow to use an alternative temporary storage, by specifying the new
  `zodb-temporary-storage` option.
  [jensens]

- Added `environment-vars` option to set environment variables. Changed
  the zope-conf-additional example code to something that isn't covered by
  the recipe.
  [claytron]

2.0 (2008-05-29)
----------------

- Do not use system but exec when starting Zope. This makes it possible for
  process management tools to properly manage Zope processes.
  [wichert]

- Added `site-zcml` option
  Added tests
  [mustapha]

- Add support for ZEO authentication. Note that this does not work with any
  released Zope or ZODB version at this moment. See
  http://mail.zope.org/pipermail/zope/2005-October/161951.html for required
  patches.
  [wichert]

- Added FTP and WebDAV options
  [claytron]

- Allow rel-storage to be an empty string, meaning 'do not use relstorage'.
  This allows an extending buildout configuration to disable relstorage again.
  [mj]

1.9 (2008-04-15)
----------------

- Fix rel-storage parsing for options with spaces. Note that split() or
  split(None) already strips the string.
  [mj]

1.8 (2008-04-05)
----------------

- Fixed a Win32 problem in which the presence of Python string escapes in the
  path to zope.conf (e.g., d:\botest\parts\instance\etc\zope.conf would escape
  the \b). This showed up when using the 'run', 'debug' or 'adduser' commands.
  This fixes #211416.
  [smcmahon]

- Added `console` command to the instance script, which is equivalent to fg but
  does not implicitly turn on debug mode but respects the zope.conf setting.
  [hannosch]

1.7 (2008-03-31)
----------------

- Added new client-home option and let it default to a subfolder of the
  buildout-wide var folder with a subfolder of the name of the section.
  [hannosch]

- Added limited support for running tests under Zope <= 2.8.
  [hannosch]

1.6 (2008-03-27)
----------------

- Fixed runzope script generation for Zope 2.8.
  [hannosch]

- Cleaned up "./bin/instance test" option handling.
  [stefan]

- Removed generator expressions as these aren't supported in < py2.4, which is
  used by zope 2.7/8.
  [duffyd]

1.5 (2008-02-29)
----------------

- Added `access-log-custom` option to be able to use another event logger
  than the file one for the access logger.
  [tarek]

- Fix instance generation to work on Windows with blanks in the path name.
  This closes #188023.
  [hannosch, gotti]

- Added 'zeo-client-client' option which results in 'client <value>' inside
  <zeoclient>.
  [timte, hannosch]

- Made relstorage handling more generic, so it now supports any RelStorage
  adapter, including Oracle (which was broken).
  [mj]

1.4 (2008-02-23)
----------------

- Fix typo in event log parameter name (from "z-log" to "z2-log"), to comply
  with the documentation. This closes #190943.
  [kdeldycke]

- Create pid and lock file folders if they don't exist.
  [kdeldycke]

- Remove hard-coded log level and use the event_log_level parameter to set it
  dynamically. This closes #190994.
  [kdeldycke]

- Added a test environment, using zc.buildout.testing, and a doctest that
  tries the recipe.
  [tarek]

- Added an `event-log-custom` option
  [tarek]

- Added example for the zope-conf-additional option. This closes #185539.
  [klm, hannosch]

- Added `rel-storage` option to be able to wire Zope to RelStorage
  (postgresql/oracle) instead of a FileStorage database.
  [tarek]

1.3
---

- For each entry in recipe-specified 'extra-paths' line, add a 'path' line
  to the instance and Zope client zope.conf files.
  [klm]

1.2
---

- Added the boolean `shared-blob` option, defaulting to `no`. If all of
  `zeo-client`, `blob-storage` and `shared-blob` options are set,
  the instance will assume the blob directory set by `blob-storage` is shared
  with the server instead of streaming 'blob' files through the ZEO connection.
  [rochael]

- Changed `ctl.do_foreground()` (which is invoked by the `fg` command
  line argument) start Zope in debug mode to emulate the behavior of
  `zopectl fg`. This required a little special WIN32 code to make
  sure it would work in both `*nix` and Windows.
  [smcmahon]

- Added `var` option, which is used to configure the base directory for all
  the things going into var.
  [hannosch]

- Added `zeo-var` option, which is used in the zeo storage snippets to
  configure the zeo var folder.
  [hannosch]

- Merged rochael-blobsupport branch. Added support for ZODB 3.8 blob storage
  configuration for ZEO clients. This references
  https://bugs.launchpad.net/collective.buildout/+bug/179113.
  [rochael, hannosch]

- Added `zeo-client-name` option. Defaults to the name of the ZEO client.
  [hannosch]

1.1
---

- Small documentation update. Added link to the bugtracker.
  [hannosch]

- Changed default of zope.conf option 'default-zpublisher-encoding' to 'utf-8'
  instead of Zope's default value of 'iso-8859-15'.

- Have PID file's location default to '${buildout:directory}/var/${name}.pid'.
  Keeping the PID file in $INSTANCE_HOME gives trouble when buildout rebuilds
  the part.
  [nouri, mustapha]

1.0
---

- Increased 'zodb_cache_size' default value to 5000, which is more likely a
  better default these days.
  [hannosch]

- Added support for 'extra-paths' as in 'zc.recipe.egg'; this is useful when
  using regular python packages for which no eggs are available (yet), i.e.
  with 'plone.recipe.distros'.
  [witsch]

- Added zeo-storage option (merge branch ree-add-zeo-storage-option).
  [ree]

- Avoid doubled entries to eggs specified in the buildout in 'sys.path':
  the working set ('ws') gets passed again when installing the script
  ('bin/instance'), but it is not also added to 'extra_paths'.
  [witsch]

- Patching 'PYTHONPATH' in the Zope startup skripts should insert all
  additional paths (to eggs) __before__ 'SOFTWARE_HOME', because otherwise
  (newer) egg versions of components from the standard Zope distribution
  (i.e. stuff that lives in 'lib/python') cannot be used.
  [witsch]

- Changed the option to suppress deprecation warnings to "--nowarn" or
  '--nowarning" to be consistent with "zopectl test".
  [witsch]

- Added option "-w" to allow the test runner to suppress deprecation warnings,
  so it's easier to spot failing tests...
  [witsch]

- Updated import for Zope 2.7 (and below) compatibility.
  [duffyd]

- Merging -r51966:52659 claytron-zopeconfoptions branch to trunk.
  [claytron]

- Made the config snippet prettier while still getting the resulting
  indentation right.
  [witsch]

0.9
---

- Added support for zodb 3.8's "<blobstorage>" directive.
  [witsch]

- Added a script name arg before callint zope.testing.testrunner.run.
  zope.testing.testrunner:1772, get_options removes the first arg from
  the list of arguments expecting a script name there. Was causing
  "bin/instance test" to behave improperly.
  [rossp]

0.8
---

- Use bin if present falling back to utilities. This makes it possible to use
  a Zope version installed from a tarball and not compiled inplace.
  [rossp]

0.7
---

- Found the problem with strange environment variables.
  [hannosch]

- Fixed documentation bug, the cache size is respected by non-zeo instance as
  well.
  [hannosch]

0.6
---

- J1m actually read the docs ;)
  [hannosch]

- Attempt to fix the sometimes insane number of tests which are found by the
  test runner.
  [hannosch]

0.5
---

- Added an option to set the effective-user.
  [optilude]

0.4
---

- Generate a bin/repozo script to perform backups using repozo.py (and
  set up the appropriate pythonpath for this to work).
  [optilude]

- Document options properly, and add the ability to specify a zope.conf
  file explicitly rather than having one generated from a template.
  [optilude]

0.3
---

- Finally found a way to provide the Zope Windows service with the right
  environment. We need a new wrapper script, which sets up the PYTHONPATH.
  [hannosch]

- Make it possible to configure the name of the zopectl script using the
  control-script option in the [instance] section.
  [wichert]

0.2
---

- Extend support for zcml slugs to include Zope 2.9.
  [dunny]

- Added support for making a ZEO-client.
  [regebro]

0.1
---

- Initial implementation.
  [hannosch]
