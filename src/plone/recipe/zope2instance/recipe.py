# ##############################################################################
#
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from plone.recipe.zope2instance import make
from warnings import warn
from zc.recipe.egg.egg import Egg
from zc.recipe.egg.egg import Scripts

import configparser
import os
import os.path
import re
import shutil
import sys
import zc.buildout
import zc.buildout.easy_install


IS_WIN = sys.platform[:3].lower() == "win"


def indent(snippet, amount):
    ws = " " * amount
    return "\n".join(ws + s if s else "" for s in snippet.split("\n"))


def nocomments_split(s):
    r"""
    Split a multiline string, skipping comments.

    >>> f = nocomments_split
    >>> f('''one.two three
    ... # ignored comment line
    ... four # ignored trailing comment
    ...    # another comment line
    ... five
    ... ''')
    ['one.two', 'three', 'four', 'five']
    >>> f('  \t')
    []
    >>> f('  # ignored')
    []

    Mixed eol styles don't matter:
    >>> f('one\r\n  # ignored \rtwo \n  # another comment\n three')
    ['one', 'two', 'three']
    """
    res = []
    for line in s.splitlines():
        if "#" in line:
            line, comment = line.split("#", 1)
        for word in line.split():
            res.append(word)
    return res


class Recipe(Scripts):
    def __init__(self, buildout, name, options):
        self.egg = Egg(buildout, options["recipe"], options)
        self.buildout, self.options, self.name = buildout, options, name
        self.scripts = True

        options["location"] = os.path.join(
            buildout["buildout"]["parts-directory"],
            self.name,
        )
        options["bin-directory"] = buildout["buildout"]["bin-directory"]

        if "scripts" in options:
            if options["scripts"] == "":
                options["scripts"] = ""  # suppress script generation.
                self.scripts = False

        # Relative path support for the generated scripts
        relative_paths = options.get(
            "relative-paths", buildout["buildout"].get("relative-paths", "false")
        )
        if relative_paths == "true":
            options["buildout-directory"] = buildout["buildout"]["directory"]
            self._relative_paths = options["buildout-directory"]
        else:
            self._relative_paths = ""

        if "initialization" not in options:
            options["initialization"] = ""
        options["initialization"] = options["initialization"] % options

        self._include_site_packages = options.get(
            "include-site-packages",
            buildout["buildout"].get("include-site-packages", "false"),
        ) not in ("off", "disable", "false")

        self.wsgi = True
        self.wsgi_config = os.path.join(options["location"], "etc", "wsgi.ini")
        wsgi_opt = options.get("wsgi", "on")
        if wsgi_opt.lower() not in ("on", "true", "1"):
            self.wsgi_config = wsgi_opt

        if "pipeline" not in options:
            options["pipeline"] = (
                """
                translogger
                egg:Zope#httpexceptions
                zope
            """.strip()
            )

        # Get Scripts' attributes
        return Scripts.__init__(self, buildout, name, options)

    def install(self, update=False):
        options = self.options
        location = options["location"]
        installed = [location]

        if not update:
            if os.path.exists(location):
                shutil.rmtree(location)

            # We could check which Zope version we have.
            # But we support creating instances for Zope 4 only.
            # Actually: version 5 only, but there is no difference in the skeleton.
            version = "4"
            make.make_instance(options.get("user", None), location, version)

        try:
            # Make a new zope.conf and wsgi.ini
            # based on options in buildout.cfg
            self.build_zope_conf()
            if self.wsgi:
                self.build_wsgi_ini()

            # Install extra scripts
            installed.extend(self.install_scripts())

            # Add zcml files to package-includes
            self.build_package_includes()
        except Exception:
            # clean up
            if os.path.exists(location):
                shutil.rmtree(location)
            raise

        if self.scripts:
            retval = Scripts.install(self)
            retval.extend(installed)
        else:
            retval = installed
        return retval

    def update(self):
        return self.install(update=True)

    def build_zope_conf(self):
        """Create a zope.conf file."""
        options = self.options
        location = options["location"]
        # Don't do this if we have a manual zope.conf
        zope_conf_path = options.get("zope-conf", None)
        if zope_conf_path is not None:
            return

        imports = options.get("zope-conf-imports", "")
        if imports:
            imports = imports.split("\n")
            # Filter out empty lines
            imports = [i for i in imports if i]
        imports_lines = "\n".join("%%import %s" % i for i in imports)

        products = options.get("products", "")
        if products:
            products = products.split("\n")
            # Filter out empty directories
            products = [p for p in products if p]
            # Make sure we have consistent path seperators
            products = [os.path.abspath(p) for p in products]

        base_dir = self.buildout["buildout"]["directory"]
        var_dir = options.get("var", os.path.join(base_dir, "var"))
        if not os.path.exists(var_dir):
            os.makedirs(var_dir)

        instance_home = location
        client_home = options.get("client-home", os.path.join(var_dir, self.name))
        if not os.path.exists(client_home):
            os.makedirs(client_home)

        client_import = options.get(
            "import-directory", os.path.join(client_home, "import")
        )
        if not os.path.exists(client_import):
            os.makedirs(client_import)

        products_lines = "\n".join(["products %s" % p for p in products])
        module_paths = options.get("extra-paths", "")
        if module_paths:
            module_paths = module_paths.split("\n")
            # Filter out empty directories
            module_paths = [p for p in module_paths if p]
            # Make sure we have consistent path seperators
            module_paths = [os.path.abspath(p) for p in module_paths]
        paths_lines = "\n".join(["path %s" % p for p in module_paths])
        debug_mode = options.get("debug-mode", "off")
        debug_exceptions = options.get("debug-exceptions", "")
        if debug_exceptions:
            debug_exceptions = debug_exceptions_template % debug_exceptions
        security_implementation = "C"
        verbose_security = options.get("verbose-security", "off")
        if verbose_security == "on":
            security_implementation = "python"
        port_base = options.get("port-base", "")
        if port_base:
            port_base = "port-base %s" % port_base
        http_force_connection_close = options.get("http-force-connection-close", None)
        if http_force_connection_close is None:
            http_force_connection_close = ""
        else:
            http_force_connection_close = (
                http_force_connection_close_template % http_force_connection_close
            )
        http_fast_listen = options.get("http-fast-listen", "on") or ""
        if http_fast_listen.lower() in ("on", "true"):
            http_fast_listen = http_fast_listen_template % "on"
        else:
            http_fast_listen = http_fast_listen_template % "off"
        http_address = options.get("http-address", "8080")
        if http_address:
            http_address = http_server_template % dict(
                http_address=http_address,
                http_force_connection_close=http_force_connection_close,
                http_fast_listen=http_fast_listen,
            )
        ftp_address = options.get("ftp-address", "")
        if ftp_address:
            ftp_address = ftp_server_template % ftp_address
        webdav_address = options.get("webdav-address", "")
        if webdav_address:
            webdav_conn_close = options.get("webdav-force-connection-close", "off")
            webdav_address = webdav_server_template % (
                webdav_address,
                webdav_conn_close,
            )
        icp_address = options.get("icp-address", "")
        if icp_address:
            icp_address = icp_server_template % icp_address
        http_header_max_length = options.get("http-header-max-length", "8192")
        if http_header_max_length:
            http_header_max_length = (
                "http-header-max-length %s" % http_header_max_length
            )
        effective_user = options.get("effective-user", "")
        if effective_user:
            effective_user = "effective-user %s" % effective_user
        ip_address = options.get("ip-address", "")
        if ip_address:
            ip_address = "ip-address %s" % ip_address

        environment_vars = options.get("environment-vars", "")

        if "CHAMELEON_CACHE" in environment_vars:
            # We do not override a explicitly defined CHAMELEON_CACHE setting!
            # Do not create the directory here because this is probably a old
            # setting and we don't want to mess with peoples working setup.
            chameleon_cache = None
        else:
            # Use template-cache setting, default to on
            chameleon_cache = options.get("template-cache", "on")

        if chameleon_cache:
            if chameleon_cache.lower() in ("on", "1", "true", "enabled"):
                # use default setting var_dir/cache
                chameleon_cache = os.path.join(var_dir, "cache")
            elif chameleon_cache.lower() in ("off", "0", "false", "disabled"):
                # disable cache
                chameleon_cache = None
            else:
                # use the passed directory, cache is enabled
                pass

        # create the cache dir if cache is enabled
        if chameleon_cache and not os.path.exists(chameleon_cache):
            os.makedirs(chameleon_cache)

        # Inject cache into environment_vars unless it is set there
        if chameleon_cache and "CHAMELEON_CACHE" not in environment_vars:
            chameleon_cache = f"CHAMELEON_CACHE {chameleon_cache}"
            if environment_vars and "\n" in environment_vars:
                # default case
                environment_vars += f"\n{chameleon_cache}"
            elif environment_vars:
                # handle case of all vars in one line
                environment_vars += f" {chameleon_cache}"
            else:
                # handle case when there are no environment_vars yet
                environment_vars = chameleon_cache

        if environment_vars:
            # if the vars are all given on one line we need to do some work
            if "\n" not in environment_vars:
                keys = []
                values = []
                env_vars = environment_vars.split()
                # split out the odd and even items into keys, values
                for var in env_vars:
                    if divmod(env_vars.index(var) + 1, 2)[1]:
                        keys.append(var)
                    else:
                        values.append(var)
                env_vars = zip(keys, values)
                environment_vars = "\n".join(
                    [f"{env_var[0]} {env_var[1]}" for env_var in env_vars]
                )
            environment_vars = environment_template % environment_vars

        deprecation_warnings = options.get("deprecation-warnings", "")
        if deprecation_warnings:
            if deprecation_warnings.lower() in ("off", "disable", "false"):
                deprecation_warnings = "ignore"
            elif deprecation_warnings.lower() in ("enable", "on", "true"):
                deprecation_warnings = "default"
            deprecation_warnings = "\n".join(
                (
                    "<warnfilter>",
                    "  action %s" % deprecation_warnings,
                    "  category DeprecationWarning",
                    "</warnfilter>",
                )
            )

        zope_conf_additional = options.get("zope-conf-additional", "")

        # logging

        mailinglogger_config = options.get("mailinglogger", "")
        mailinglogger_import = ""
        if mailinglogger_config:
            mailinglogger_config = mailinglogger_config.strip()
            mailinglogger_import = "%import mailinglogger"

        default_log = os.path.sep.join(
            (
                "log",
                self.name + ".log",
            )
        )
        event_log_name = options.get("event-log", default_log)

        if event_log_name.lower() == "disable":
            event_log = ""
        else:
            event_log_level = options.get("event-log-level", "INFO")
            custom_event_log = options.get("event-log-custom", None)
            # log file
            if not custom_event_log:
                event_file = os.path.join(var_dir, event_log_name)
                event_log_dir = os.path.dirname(event_file)
                if not os.path.exists(event_log_dir):
                    os.makedirs(event_log_dir)
                event_log_rotate = ""
                event_log_max_size = options.get("event-log-max-size", None)
                if event_log_max_size:
                    event_log_old_files = options.get("event-log-old-files", 1)
                    event_log_rotate = "\n".join(
                        (
                            "max-size %s" % event_log_max_size,
                            "    old-files %s" % event_log_old_files,
                        )
                    )
                event_log = event_logfile % {
                    "event_logfile": event_file,
                    "event_log_level": event_log_level,
                    "event_log_rotate": event_log_rotate,
                }
            # custom log
            else:
                event_log = custom_event_log

            event_log = event_log_template % {
                "mailinglogger_config": mailinglogger_config,
                "event_log_level": event_log_level,
                "event_log": event_log,
            }

        z_log_name = os.path.sep.join(("log", self.name + "-Z2.log"))
        z_log_name = options.get("z2-log", options.get("access-log", z_log_name))
        if z_log_name.lower() == "disable":
            access_event_log = ""
        else:
            z_log = os.path.join(var_dir, z_log_name)
            z_log_dir = os.path.dirname(z_log)
            if not os.path.exists(z_log_dir):
                os.makedirs(z_log_dir)

            z_log_level = options.get("z2-log-level", "WARN")

            # access event log
            custom_access_event_log = options.get("access-log-custom", None)
            # filelog directive
            if not custom_access_event_log:
                access_log_rotate = ""
                access_log_max_size = options.get("access-log-max-size", None)
                if access_log_max_size:
                    access_log_old_files = options.get("access-log-old-files", 1)
                    access_log_rotate = "\n".join(
                        (
                            "max-size %s" % access_log_max_size,
                            "    old-files %s" % access_log_old_files,
                        )
                    )
                access_event_log = access_event_logfile % {
                    "z_log": z_log,
                    "access_log_rotate": access_log_rotate,
                }
            # custom directive
            else:
                access_event_log = custom_access_event_log

            access_event_log = access_log_template % {
                "z_log_level": z_log_level,
                "access_event_log": access_event_log,
            }

        default_zpublisher_encoding = options.get(
            "default-zpublisher-encoding", "utf-8"
        )
        if default_zpublisher_encoding:
            default_zpublisher_encoding = (
                "default-zpublisher-encoding %s" % default_zpublisher_encoding
            )

        zeo_client = options.get("zeo-client", "")
        zeo_client = zeo_client.lower() in ("yes", "true", "on", "1")
        shared_blob_dir = options.get("shared-blob", "no")

        before_storage = options.get("before-storage")
        demo_storage = options.get("demo-storage", "off") not in (
            "off",
            "disable",
            "false",
        )

        zlib = options.get("zlib-storage")

        default_blob = os.path.join(var_dir, "blobstorage")
        default_file = os.path.sep.join(
            (
                "filestorage",
                "Data.fs",
            )
        )

        # Don't try to use the actual blobstorage as a cache
        if zeo_client and shared_blob_dir == "no":
            default_blob = os.path.join(var_dir, "blobcache")

        # Only set blob storage default if we're using a before
        # storage, or not a demo storage (otherwise, the default
        # would be an invalid setting)
        if demo_storage and not before_storage:
            default_blob = None

        blob_storage = options.get("blob-storage", default_blob)
        file_storage = options.get("file-storage", default_file)

        relstorage = options.get("rel-storage")
        if relstorage:

            def _split(el):
                el = el.split(None, 1)
                return len(el) == 2 and el or None

            rel_storage = dict(
                [_split(el) for el in relstorage.splitlines() if _split(el) is not None]
            )
            type_ = rel_storage.pop("type", "postgresql")

            if type_ == "postgresql" and "dsn" not in rel_storage:
                # Support zope2instance 1.4 style interpolation for
                # postgresql
                template = (
                    "dbname='%(dbname)s' user='%(user)s' "
                    "host='%(host)s' password='%(password)s'"
                )
                dsn = template % rel_storage
                del rel_storage["dbname"]
                del rel_storage["user"]
                del rel_storage["host"]
                del rel_storage["password"]
                rel_storage["dsn"] = dsn

            def is_rs_option(name):
                # All generic RelStorage options have a dash in their name,
                # except the "name" option. Other options are
                # database-specific.
                if name == "data-dir":  # sqlite3
                    return False
                return "-" in name or name == "name"

            db_opts = "\n".join(
                " " * 12 + " ".join((k, v))
                for k, v in rel_storage.items()
                if not is_rs_option(k)
            )
            if type_ == "sqlite3":
                pragmas = [k for k in rel_storage if k.startswith("pragmas-")]
                if pragmas:
                    db_opts += "\n" + " " * 12 + "<pragmas>\n"
                    for k in sorted(pragmas):
                        db_opts += " " * 16 + " ".join((k[8:], rel_storage[k])) + "\n"
                        del rel_storage[k]
                    db_opts += " " * 12 + "</pragmas>\n"
            opts = dict(
                type=type_,
                db_opts=db_opts,
                rs_opts="\n".join(
                    " " * 8 + " ".join((k, v))
                    for k, v in rel_storage.items()
                    if is_rs_option(k)
                ),
            )
            file_storage_snippet = rel_storage_template % opts
        else:
            file_storage_snippet = self.render_file_storage(
                file_storage, blob_storage, base_dir, var_dir, zlib
            )

        if "zserver-threads" in options:
            warn(
                'option "zserver-threads" is deprecated, please use "threads"',
                DeprecationWarning,
            )
        zserver_threads = options.get("threads", options.get("zserver-threads", "2"))
        if zserver_threads:
            zserver_threads = "zserver-threads %s" % zserver_threads

        python_check_interval = options.get("python-check-interval", "1000")
        if python_check_interval:
            python_check_interval = "python-check-interval %s" % python_check_interval

        enable_products = options.get("enable-product-installation", "off")
        if enable_products:
            enable_products = "enable-product-installation %s" % enable_products

        zeo_address = options.get("zeo-address", "8100")
        zeo_addresses = zeo_address.split(" ")
        zeo_address_list = ""
        for address in zeo_addresses:
            if not address:
                continue
            zeo_address_list += zeo_address_list_template % dict(zeo_address=address)

        zodb_cache_size = options.get("zodb-cache-size", "30000")
        if zodb_cache_size:
            zodb_cache_size = "cache-size %s" % zodb_cache_size
        else:
            zodb_cache_size = ""
        zodb_cache_size_bytes = options.get("zodb-cache-size-bytes", None)
        if zodb_cache_size_bytes:
            zodb_cache_size_bytes = "cache-size-bytes %s" % zodb_cache_size_bytes
        else:
            zodb_cache_size_bytes = ""
        zeo_client_cache_size = options.get("zeo-client-cache-size", "128MB")
        zeo_storage = options.get("zeo-storage", "1")

        if zeo_client:
            if relstorage:
                raise ValueError(
                    "You cannot use both ZEO and RelStorage at the same time."
                )

            zeo_client_drop_cache_rather_verify = options.get(
                "zeo-client-drop-cache-rather-verify", ""
            )
            if zeo_client_drop_cache_rather_verify:
                zeo_client_drop_cache_rather_verify = (
                    "drop-cache-rather-verify %s" % zeo_client_drop_cache_rather_verify
                )
            zeo_client_blob_cache_size = options.get("zeo-client-blob-cache-size", "")
            zeo_client_blob_cache_size_check = options.get(
                "zeo-client-blob-cache-size-check", ""
            )
            zeo_client_min_disconnect_poll = options.get("min-disconnect-poll", "")
            zeo_client_max_disconnect_poll = options.get("max-disconnect-poll", "")
            zeo_client_read_only_fallback = options.get(
                "zeo-client-read-only-fallback", "false"
            )
            zeo_client_client = options.get("zeo-client-client", "")
            if zeo_client_client:
                zeo_client_client = "client %s" % zeo_client_client
                zeo_var_dir = options.get("zeo-var", "")
                if not zeo_var_dir:
                    zeo_var_dir = "$(ZEO_TMP)"
                zeo_var_dir = "var %s" % zeo_var_dir
            else:
                zeo_var_dir = ""
            if zeo_client_blob_cache_size:
                zeo_client_blob_cache_size = (
                    "blob-cache-size %s" % zeo_client_blob_cache_size
                )
            if zeo_client_blob_cache_size_check:
                zeo_client_blob_cache_size_check = (
                    "blob-cache-size-check %s" % zeo_client_blob_cache_size_check
                )
            if zeo_client_min_disconnect_poll:
                zeo_client_min_disconnect_poll = (
                    "min-disconnect-poll %s" % zeo_client_min_disconnect_poll
                )
            if zeo_client_max_disconnect_poll:
                zeo_client_max_disconnect_poll = (
                    "max-disconnect-poll %s" % zeo_client_max_disconnect_poll
                )
            if zeo_client_read_only_fallback:
                zeo_client_read_only_fallback = (
                    "read-only-fallback %s" % zeo_client_read_only_fallback
                )
            if options.get("zeo-username", ""):
                if not options.get("zeo-password", ""):
                    raise zc.buildout.UserError("No ZEO password specified")

                zeo_authentication = zeo_authentication_template % dict(
                    realm=options.get("zeo-realm", "ZEO"),
                    username=options.get("zeo-username"),
                    password=options.get("zeo-password"),
                )
            else:
                zeo_authentication = ""

            if blob_storage:
                storage_snippet_template = zeo_blob_storage_template
            else:
                storage_snippet_template = zeo_storage_template

            storage_snippet = storage_snippet_template % dict(
                blob_storage=blob_storage,
                shared_blob_dir=shared_blob_dir,
                zeo_address_list=zeo_address_list,
                zeo_client_cache_size=zeo_client_cache_size,
                zeo_client_blob_cache_size=zeo_client_blob_cache_size,
                zeo_client_blob_cache_size_check=zeo_client_blob_cache_size_check,  # noqa: E501
                zeo_authentication=zeo_authentication,
                zeo_client_client=zeo_client_client,
                zeo_storage=zeo_storage,
                zeo_var_dir=zeo_var_dir,
                zeo_client_drop_cache_rather_verify=zeo_client_drop_cache_rather_verify,  # noqa: E501
                zeo_client_min_disconnect_poll=zeo_client_min_disconnect_poll,
                zeo_client_max_disconnect_poll=zeo_client_max_disconnect_poll,
                read_only=options.get("read-only", "false"),
                zeo_client_read_only_fallback=zeo_client_read_only_fallback,
            )
        else:
            # no zeo-client
            zeo_client_client = ""
            storage_snippet = file_storage_snippet

        if before_storage:
            storage_snippet = (before_storage_template % before_storage) % indent(
                storage_snippet, 2
            )

        if demo_storage:
            demo_file_storage = options.get("demo-file-storage")
            demo_blob_storage = options.get("demo-blob-storage")

            if demo_file_storage or demo_blob_storage:
                base = storage_snippet.replace(">", " base>", 1)
                changes = self.render_file_storage(
                    demo_file_storage, demo_blob_storage, base_dir, var_dir, zlib
                ).replace(">", " changes>", 1)

                storage_snippet = demo_storage2_template % (base, changes)

            elif "blob-storage" in options:
                raise ValueError(
                    "Both blob and demo storage cannot be used"
                    " at the same time (use a before storage instead)."
                )
            else:
                storage_snippet = demo_storage_template % storage_snippet

        if options.get("storage-wrapper"):
            storage_snippet = indent(options["storage-wrapper"] % storage_snippet, 4)

        zodb_tmp_storage = options.get("zodb-temporary-storage")
        if zodb_tmp_storage is None:
            # What should be the default?  In Plone 6 or higher (which are the only
            # Plone versions the recipe supports) we do not want to use the temporary
            # storage anymore.  So look for the main package Products.CMFPlone
            # See https://github.com/plone/plone.recipe.zope2instance/issues/180
            requirements, ws = self.egg.working_set(["plone.recipe.zope2instance"])
            # It is anyone's guess by which key Products.CMFPlone may be known.
            # This depends on the setuptools and zc.buildout versions.
            cmfplone = (
                ws.by_key.get("products-cmfplone")
                or ws.by_key.get("products.cmfplone")
                or ws.by_key.get("Products.CMFPlone")
            )
            if cmfplone:
                zodb_tmp_storage = "off"
            else:
                zodb_tmp_storage = "on"
        if zodb_tmp_storage.lower() in ("off", "false", "0"):
            # no temporary-storage snippet
            zodb_tmp_storage = ""
        elif zodb_tmp_storage.lower() in ("on", "true", "1"):
            # use default temporary-storage snippet
            zodb_tmp_storage = zodb_temporary_storage_template
        template = wsgi_conf_template if self.wsgi else zope_conf_template

        pid_file = options.get("pid-file", os.path.join(var_dir, self.name + ".pid"))
        pid_file_dir = os.path.dirname(pid_file)
        if not os.path.exists(pid_file_dir):
            os.makedirs(pid_file_dir)

        lock_file = options.get("lock-file", os.path.join(var_dir, self.name + ".lock"))
        lock_file_dir = os.path.dirname(lock_file)
        if not os.path.exists(lock_file_dir):
            os.makedirs(lock_file_dir)

        zope_conf = template % dict(
            instance_home=instance_home,
            client_home=client_home,
            imports_lines=imports_lines,
            paths_lines=paths_lines,
            products_lines=products_lines,
            debug_mode=debug_mode,
            debug_exceptions=debug_exceptions,
            security_implementation=security_implementation,
            verbose_security=verbose_security,
            effective_user=effective_user,
            http_header_max_length=http_header_max_length,
            ip_address=ip_address,
            mailinglogger_import=mailinglogger_import,
            event_log=event_log,
            access_event_log=access_event_log,
            default_zpublisher_encoding=default_zpublisher_encoding,
            storage_snippet=storage_snippet,
            port_base=port_base,
            http_address=http_address,
            http_force_connection_close=http_force_connection_close,
            http_fast_listen=http_fast_listen,
            ftp_address=ftp_address,
            webdav_address=webdav_address,
            icp_address=icp_address,
            zserver_threads=zserver_threads,
            zodb_cache_size=zodb_cache_size,
            zodb_cache_size_bytes=zodb_cache_size_bytes,
            zodb_tmp_storage=zodb_tmp_storage,
            pid_file=pid_file,
            lock_file=lock_file,
            environment_vars=environment_vars,
            deprecation_warnings=deprecation_warnings,
            python_check_interval=python_check_interval,
            enable_products=enable_products,
            zope_conf_additional=zope_conf_additional,
        )

        zope_conf = "\n".join(
            [line for line in zope_conf.splitlines() if line.rstrip()]
        )
        zope_conf_path = os.path.join(location, "etc", "zope.conf")
        with open(zope_conf_path, "w") as f:
            f.write(zope_conf)

    def build_wsgi_ini(self):
        options = self.options
        wsgi_ini_path = os.path.join(options["location"], "etc", "wsgi.ini")
        listen = options.get("http-address", "0.0.0.0:8080")
        fast_listen = options.get("http-fast-listen", "on") or ""
        fast = "fast-" if fast_listen.lower() in ("on", "true") else ""
        listen = " ".join(
            [f"0.0.0.0:{part}" if ":" not in part else part for part in listen.split()]
        )
        base_dir = self.buildout["buildout"]["directory"]
        var_dir = options.get("var", os.path.join(base_dir, "var"))
        default_eventlog = os.path.sep.join(
            (
                var_dir,
                "log",
                f"{self.name}.log",
            )
        )
        eventlog_name = options.get("event-log", default_eventlog)
        eventlog_level = options.get("event-log-level", "INFO")
        eventlog_handler = options.get("event-log-handler", "FileHandler")
        eventlog_kwargs = options.get("event-log-kwargs", "{}")
        eventlog_args = options.get("event-log-args")
        if not eventlog_args:
            eventlog_args = f"(r'{eventlog_name}', 'a')"
        else:
            eventlog_args = eventlog_args.format(eventlog_name)

        if eventlog_name.lower() == "disable":
            root_handlers = "console"
            event_handlers = ""
        else:
            root_handlers = "console, eventlog"
            event_handlers = "eventlog"

        default_accesslog = os.path.sep.join(
            (
                var_dir,
                "log",
                f"{self.name}-access.log",
            )
        )

        accesslog_name = options.get(
            "z2-log", options.get("access-log", default_accesslog)
        )
        accesslog_level = options.get(
            "access-log-level", options.get("z2-log-level", "INFO")
        )
        accesslog_handler = options.get("access-log-handler", "FileHandler")
        accesslog_kwargs = options.get("access-log-kwargs", "{}")
        accesslog_args = options.get("access-log-args")
        if not accesslog_args:
            accesslog_args = f"(r'{accesslog_name}', 'a')"
        else:
            accesslog_args = accesslog_args.format(accesslog_name)

        pipeline = options["pipeline"].split()
        if accesslog_name.lower() == "disable":
            event_handlers = ""
            accesslog_handler = "NullHandler"
            accesslog_args = "()"
            pipeline = [line for line in pipeline if line != "translogger"]

        sentry_dsn = options.get("sentry_dsn", "")
        if sentry_dsn:
            if "zope" in pipeline:
                pipeline.insert(pipeline.index("zope"), "sentry")
            else:
                pipeline.append("sentry")
        sentry_level = options.get("sentry_level", "INFO")
        sentry_event_level = options.get("sentry_event_level", "ERROR")
        sentry_ignore = options.get("sentry_ignore", "")
        sentry_max_value_length = options.get("sentry_max_value_length", "")

        profile = options.get("profile", "").strip() == "on"
        if profile:
            if "zope" in pipeline:
                pipeline.insert(pipeline.index("zope"), "profile")
            else:
                pipeline.append("profile")
        default_profile_log_filename = os.path.sep.join(
            [
                var_dir,
                "log",
                f"profile-{self.name}.raw",
            ]
        )
        profile_log_filename = options.get(
            "profile_log_filename", default_profile_log_filename
        )
        default_profile_log_filename = os.path.sep.join(
            [
                var_dir,
                "log",
                f"cachegrind.out.{self.name}",
            ]
        )
        profile_cachegrind_filename = options.get(
            "profile_cachegrind_filename", default_profile_log_filename
        )
        profile_discard_first_request = options.get(
            "profile_discard_first_request", "true"
        )
        profile_path = options.get("profile_path", "/__profile__")
        profile_flush_at_shutdown = options.get("profile_flush_at_shutdown", "true")
        profile_unwind = options.get("profile_unwind", "false")

        if "zope" not in pipeline:
            pipeline.append("zope")

        wsgi_options = {
            "accesslog_args": accesslog_args,
            "accesslog_handler": accesslog_handler,
            "accesslog_kwargs": accesslog_kwargs,
            "accesslog_level": accesslog_level,
            "accesslog_name": accesslog_name,
            "asyncore_use_poll": (
                "true"
                if options.get("asyncore-use-poll", "false").lower() in ("on", "true")
                else "false"
            ),
            "clear_untrusted_proxy_headers": options.get(
                "clear-untrusted-proxy-headers", "false"
            ),
            "event_handlers": event_handlers,
            "eventlog_args": eventlog_args,
            "eventlog_handler": eventlog_handler,
            "eventlog_kwargs": eventlog_kwargs,
            "eventlog_level": eventlog_level,
            "eventlog_name": eventlog_name,
            "fast-listen": fast,
            "http_address": listen,
            "location": options["location"],
            "max_request_body_size": options.get("max-request-body-size", 1073741824),
            "pipeline": "\n    ".join(pipeline),
            "root_handlers": root_handlers,
            "sentry_dsn": sentry_dsn,
            "sentry_event_level": sentry_event_level,
            "sentry_ignore": sentry_ignore,
            "sentry_level": sentry_level,
            "sentry_max_value_length": sentry_max_value_length,
            "threads": options.get("threads", 4),
            "profile_log_filename": profile_log_filename,
            "profile_cachegrind_filename": profile_cachegrind_filename,
            "profile_discard_first_request": profile_discard_first_request,
            "profile_path": profile_path,
            "profile_flush_at_shutdown": profile_flush_at_shutdown,
            "profile_unwind": profile_unwind,
        }

        # Check custom wsgi-ini-template and wsgi-logging-ini-template
        wsgi_ini_template_path = self.options.get("wsgi-ini-template")
        wsgi_logging_ini_template_path = self.options.get("wsgi-logging-ini-template")
        if wsgi_ini_template_path and wsgi_logging_ini_template_path:
            raise ValueError(
                "wsgi_ini_template_path and wsgi_logging_ini_template_path "
                "cannot be used together."
            )

        # Load custom wsgi template from file
        if wsgi_ini_template_path:
            try:
                with open(wsgi_ini_template_path) as fp:
                    wsgi_ini_template = fp.read()
            except OSError:
                raise

        # Load default wsgi template and load custom wsgi logging template
        elif wsgi_logging_ini_template_path:
            wsgi_ini_template = default_wsgi_ini_template
            try:
                with open(wsgi_logging_ini_template_path) as fp:
                    # Add custom wsgi logging template to wsgi template
                    wsgi_ini_template += fp.read()
            except OSError:
                raise

        # Load default wsgi and logging templates
        else:
            wsgi_ini_template = (
                default_wsgi_ini_template + default_wsgi_logging_ini_template
            )

        assert wsgi_ini_template

        # generate a different [server:main] - useful for Windows
        wsgi_server_main_template = wsgi_server_main_templates.get(
            sys.platform, wsgi_server_main_templates["default"]
        )
        wsgi_options["server_main"] = wsgi_server_main_template % wsgi_options

        wsgi_ini = wsgi_ini_template % wsgi_options

        # Catch errors in generated wsgi.ini by parsing it before writing the file
        configparser.ConfigParser().read_string(wsgi_ini)

        with open(wsgi_ini_path, "w") as f:
            f.write(wsgi_ini)

    def install_scripts(self):
        if IS_WIN:
            # instance scripts are usung zdaemon, which are Unix only
            return {}
        options = self.options
        location = options["location"]

        # The instance control script
        zope_conf = os.path.join(location, "etc", "zope.conf")
        zope_conf_path = options.get("zope-conf", zope_conf)
        program_name = "interpreter"
        program_path = os.path.join(location, "bin", program_name)

        zopectl_umask = options.get("zopectl-umask", "")

        extra_paths = options.get("extra-paths", "").split()
        requirements, ws = self.egg.working_set(["plone.recipe.zope2instance"])
        reqs = [self.options.get("control-script", self.name)]
        reqs.extend(["plone.recipe.zope2instance.ctl", "main"])
        reqs = [tuple(reqs)]

        if options.get("relative-paths"):

            class relative_path_str(str):
                def __repr__(self):
                    return str(self)

            zope_conf_path = relative_path_str(
                zc.buildout.easy_install._relativitize(
                    zope_conf,
                    options["buildout-directory"] + os.sep,
                    self._relative_paths,
                )
            )
            program_path = relative_path_str(
                zc.buildout.easy_install._relativitize(
                    program_path,
                    options["buildout-directory"] + os.sep,
                    self._relative_paths,
                )
            )

        options["zope-conf"] = zope_conf_path
        arguments = ["-C", zope_conf_path, "-p", program_path]
        if zopectl_umask:
            arguments.extend(["--umask", int(zopectl_umask, 8)])
        if self.wsgi and self.wsgi_config:
            arguments.extend(["-w", self.wsgi_config])
        script_arguments = "\n        " + repr(arguments) + "\n        + sys.argv[1:]"

        generated = self._install_scripts(
            options["bin-directory"],
            ws,
            reqs=reqs,
            extra_paths=extra_paths,
            script_arguments=script_arguments,
        )
        generated.extend(
            self._install_scripts(
                os.path.join(options["location"], "bin"),
                ws,
                interpreter=program_name,
                extra_paths=extra_paths,
            )
        )
        return generated

    def _install_scripts(
        self,
        dest,
        working_set,
        reqs=(),
        interpreter=None,
        extra_paths=(),
        script_arguments="",
    ):
        options = self.options
        return zc.buildout.easy_install.scripts(
            dest=dest,
            reqs=reqs,
            working_set=working_set,
            executable=options["executable"],
            extra_paths=extra_paths,
            initialization=options["initialization"],
            arguments=script_arguments,
            interpreter=interpreter,
            relative_paths=self._relative_paths,
        )

    def build_package_includes(self):
        """Create ZCML slugs in etc/package-includes."""
        location = self.options["location"]
        sitezcml_path = os.path.join(location, "etc", "site.zcml")
        zcml = self.options.get("zcml")
        site_zcml = self.options.get("site-zcml")
        additional_zcml = self.options.get("zcml-additional")
        resources = self.options.get("resources")
        locales = self.options.get("locales")

        if site_zcml:
            open(sitezcml_path, "w").write(site_zcml)
            return

        if zcml:
            zcml = nocomments_split(zcml)

        if additional_zcml or resources or locales or zcml:
            includes_path = os.path.join(location, "etc", "package-includes")

            if not os.path.exists(includes_path):
                # Zope 2.9 does not have a package-includes so we
                # create one.
                os.mkdir(includes_path)
            else:
                if zcml and "*" in zcml:
                    zcml.remove("*")
                else:
                    shutil.rmtree(includes_path)
                    os.mkdir(includes_path)

        if additional_zcml:
            additional_zcml = additional_zcml_template % additional_zcml
            path = os.path.join(includes_path, "999-additional-overrides.zcml")
            open(path, "w").write(additional_zcml.strip())

        if resources:
            resources_path = resources.strip()
            path = os.path.join(includes_path, "998-resources-configure.zcml")
            open(path, "w").write(resources_zcml % dict(directory=resources_path))

            if not os.path.exists(resources_path):
                os.mkdir(resources_path)

        if locales:
            locales_path = locales.strip()
            path = os.path.join(includes_path, "001-locales-configure.zcml")
            open(path, "w").write(locales_zcml % dict(directory=locales_path))

            if not os.path.exists(locales_path):
                os.mkdir(locales_path)

        if zcml:
            n = 1  # 001 is reserved for an optional locales-configure
            package_match = re.compile(r"\w+([.]\w+)*$").match
            for package in zcml:
                n += 1
                orig = package
                if ":" in package:
                    package, filename = package.split(":")
                else:
                    filename = None

                if "-" in package:
                    package, suff = package.split("-")
                    file_suff = suff
                    if suff not in ("configure", "meta", "overrides"):
                        file_suff = "%s-configure" % suff
                else:
                    suff = file_suff = "configure"

                if filename is None:
                    filename = suff + ".zcml"

                if not package_match(package):
                    raise ValueError("Invalid zcml", orig)

                path = os.path.join(
                    includes_path,
                    "%3.3d-%s-%s.zcml" % (n, package, file_suff),
                )
                open(path, "w").write(
                    f'<include package="{package}" file="{filename}" />\n'
                )

    def render_file_storage(self, file_storage, blob_storage, base_dir, var_dir, zlib):
        if file_storage:
            file_storage = os.path.join(var_dir, file_storage)
            file_storage_dir = os.path.dirname(file_storage)
            if not os.path.exists(file_storage_dir):
                os.makedirs(file_storage_dir)
            storage = file_storage_template % file_storage
            if zlib is not None:
                if zlib == "active":
                    compress = "true"
                elif zlib == "passive":
                    compress = "false"
                else:
                    raise ValueError(
                        "Valid options for ``zlib-storage`` are "
                        "('compress', 'uncompress'). Got: %s." % zlib
                    )

                storage = zlib_storage_template % (compress, indent(storage, 2))
        else:
            storage = "    <demostorage />"

        if not blob_storage:
            return storage

        blob_storage = os.path.join(base_dir, blob_storage)
        if not os.path.exists(blob_storage):
            # Make it only readable for the current user, otherwise
            # you get a ZODB warning on startup.
            os.makedirs(blob_storage, 0o700)

        storage = indent(storage, 2)

        return blob_storage_template % (blob_storage, storage)


# Storage snippets for zope.conf template
file_storage_template = """
    # FileStorage database
    <filestorage>
      path %s
    </filestorage>
"""

zlib_storage_template = """
    %%import zc.zlibstorage
    # ZlibStorage wrapper
    <zlibstorage>
      compress %s
%s
    </zlibstorage>
"""

demo_storage_template = """
    # DemoStorage
    <demostorage>
%s
    </demostorage>
"""

before_storage_template = """
    %%%%import zc.beforestorage
    # BeforeStorage
    <before>
      before %s
  %%s
    </before>
"""

demo_storage2_template = """
    # DemoStorage
    <demostorage>
%s
%s
    </demostorage>
"""

rel_storage_template = """
    %%import relstorage
    <relstorage>
%(rs_opts)s
        <%(type)s>
%(db_opts)s
        </%(type)s>
    </relstorage>
"""

blob_storage_template = """
    # Blob-enabled FileStorage database
    <blobstorage>
      blob-dir %s
%s
    </blobstorage>
"""

zeo_authentication_template = """
    realm %(realm)s
      username %(username)s
      password %(password)s
""".strip()

zeo_address_list_template = """
      server %(zeo_address)s
"""

zeo_storage_template = """
    # ZEOStorage database
    <zeoclient>
      read-only %(read_only)s
      %(zeo_client_read_only_fallback)s
      %(zeo_address_list)s
      storage %(zeo_storage)s
      name zeostorage
      cache-size %(zeo_client_cache_size)s
      %(zeo_authentication)s
      %(zeo_var_dir)s
      %(zeo_client_client)s
      %(zeo_client_min_disconnect_poll)s
      %(zeo_client_max_disconnect_poll)s
      %(zeo_client_drop_cache_rather_verify)s
    </zeoclient>
""".strip()

zeo_blob_storage_template = """
    # Blob-enabled ZEOStorage database
    <zeoclient>
      read-only %(read_only)s
      %(zeo_client_read_only_fallback)s
      blob-dir %(blob_storage)s
      shared-blob-dir %(shared_blob_dir)s
      %(zeo_address_list)s
      storage %(zeo_storage)s
      name zeostorage
      cache-size %(zeo_client_cache_size)s
      %(zeo_client_blob_cache_size)s
      %(zeo_client_blob_cache_size_check)s
      %(zeo_authentication)s
      %(zeo_var_dir)s
      %(zeo_client_client)s
      %(zeo_client_min_disconnect_poll)s
      %(zeo_client_max_disconnect_poll)s
      %(zeo_client_drop_cache_rather_verify)s
    </zeoclient>
""".strip()

zodb_temporary_storage_template = """
<zodb_db temporary>
    # Temporary storage database (for sessions)
    <temporarystorage>
      name temporary storage for sessioning
    </temporarystorage>
    mount-point /temp_folder
    container-class Products.TemporaryFolder.TemporaryContainer
</zodb_db>
""".strip()

debug_exceptions_template = """\
debug-exceptions %s
"""

http_force_connection_close_template = """\
  force-connection-close %s
""".rstrip()

http_fast_listen_template = """\
  # Set to off to defer opening of the HTTP socket until the end of the
  # startup phase:
  fast-listen %s
""".rstrip()

event_logfile = """
  <logfile>
    path %(event_logfile)s
    level %(event_log_level)s
    %(event_log_rotate)s
  </logfile>
""".strip()

access_event_logfile = """
  <logfile>
    path %(z_log)s
    format %%(message)s
    %(access_log_rotate)s
  </logfile>
""".strip()

http_server_template = """
<http-server>
  address %(http_address)s
%(http_force_connection_close)s
%(http_fast_listen)s
</http-server>
"""

ftp_server_template = """
<ftp-server>
  # valid key is "address"
  address %s
</ftp-server>
"""

icp_server_template = """
<icp-server>
  # valid key is "address"
  address %s
</icp-server>
"""

webdav_server_template = """
<webdav-source-server>
  address %s
  force-connection-close %s
</webdav-source-server>
"""

environment_template = """
<environment>
    %s
</environment>
"""

# The template used to build zope.conf
zope_conf_template = """\
%(imports_lines)s
%%define INSTANCEHOME %(instance_home)s
instancehome $INSTANCEHOME
%%define CLIENTHOME %(client_home)s
clienthome $CLIENTHOME
%(paths_lines)s
%(products_lines)s
debug-mode %(debug_mode)s
security-policy-implementation %(security_implementation)s
verbose-security %(verbose_security)s
%(default_zpublisher_encoding)s
%(port_base)s
%(effective_user)s
%(http_header_max_length)s
%(ip_address)s
%(zserver_threads)s
%(environment_vars)s
%(deprecation_warnings)s

%(mailinglogger_import)s

%(event_log)s

%(access_event_log)s

%(http_address)s
%(ftp_address)s
%(webdav_address)s
%(icp_address)s

<zodb_db main>
    # Main database
    %(zodb_cache_size)s
    %(zodb_cache_size_bytes)s
%(storage_snippet)s
    mount-point /
</zodb_db>

%(zodb_tmp_storage)s

pid-filename %(pid_file)s
lock-filename %(lock_file)s
%(python_check_interval)s
%(enable_products)s

%(zope_conf_additional)s
"""

wsgi_conf_template = """\
%(imports_lines)s
%%define INSTANCEHOME %(instance_home)s
instancehome $INSTANCEHOME
%%define CLIENTHOME %(client_home)s
clienthome $CLIENTHOME
%(products_lines)s
debug-mode %(debug_mode)s
%(debug_exceptions)s
security-policy-implementation %(security_implementation)s
verbose-security %(verbose_security)s
%(default_zpublisher_encoding)s
%(port_base)s
%(environment_vars)s

%(mailinglogger_import)s

<zodb_db main>
    # Main database
    %(zodb_cache_size)s
    %(zodb_cache_size_bytes)s
%(storage_snippet)s
    mount-point /
</zodb_db>

%(zodb_tmp_storage)s

%(python_check_interval)s

%(zope_conf_additional)s
"""

event_log_template = """\
<eventlog>
  %(mailinglogger_config)s
  level %(event_log_level)s
  %(event_log)s
</eventlog>
"""

access_log_template = """\
<logger access>
  level %(z_log_level)s
  %(access_event_log)s
</logger>
"""

# Template used for plone.resource directory
resources_zcml = """\
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:plone="http://namespaces.plone.org/plone">
    <include package="plone.resource" file="meta.zcml"/>
    <plone:static directory="%(directory)s"/>
</configure>
"""

# Template used for locales directory
locales_zcml = """\
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:i18n="http://namespaces.zope.org/i18n">
    <i18n:registerTranslations directory="%(directory)s" />
</configure>
"""

# Template used for additional ZCML
additional_zcml_template = """\
<configure xmlns="http://namespaces.zope.org/zope">
    %s
</configure>
"""

wsgi_server_main_templates = {}
wsgi_server_main_templates[
    "default"
] = """\
paste.server_factory = plone.recipe.zope2instance:main
use = egg:plone.recipe.zope2instance#main
%(fast-listen)slisten = %(http_address)s
threads = %(threads)s
clear_untrusted_proxy_headers = %(clear_untrusted_proxy_headers)s
max_request_body_size = %(max_request_body_size)s
asyncore_use_poll = %(asyncore_use_poll)s
"""

wsgi_server_main_templates[
    "win32"
] = """\
use = egg:waitress#main
listen = %(http_address)s
threads = %(threads)s
clear_untrusted_proxy_headers = %(clear_untrusted_proxy_headers)s
max_request_body_size = %(max_request_body_size)s
"""

default_wsgi_ini_template = """\
[server:main]
%(server_main)s

[app:zope]
use = egg:Zope#main
zope_conf = %(location)s/etc/zope.conf

[filter:translogger]
use = egg:Paste#translogger
setup_console_handler = False

[filter:sentry]
use = egg:plone.recipe.zope2instance#sentry
dsn = %(sentry_dsn)s
level = %(sentry_level)s
event_level = %(sentry_event_level)s
ignorelist = %(sentry_ignore)s
max_value_length = %(sentry_max_value_length)s

[filter:profile]
use = egg:repoze.profile
log_filename = %(profile_log_filename)s
cachegrind_filename = %(profile_cachegrind_filename)s
discard_first_request = %(profile_discard_first_request)s
path = %(profile_path)s
flush_at_shutdown = %(profile_flush_at_shutdown)s
unwind = %(profile_unwind)s

[pipeline:main]
pipeline =
    %(pipeline)s

"""

default_wsgi_logging_ini_template = """\
[loggers]
keys = root, plone, waitress.queue, waitress, wsgi

[handlers]
keys = console, accesslog, eventlog

[formatters]
keys = generic, message

[logger_root]
level = %(eventlog_level)s
handlers = %(root_handlers)s

[logger_plone]
level = %(eventlog_level)s
handlers = %(event_handlers)s
qualname = plone

[logger_waitress.queue]
level = INFO
handlers = eventlog
qualname = waitress.queue
propagate = 0

[logger_waitress]
level = %(eventlog_level)s
handlers = %(event_handlers)s
qualname = waitress

[logger_wsgi]
level = %(accesslog_level)s
handlers = accesslog
qualname = wsgi
propagate = 0

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[handler_accesslog]
class = %(accesslog_handler)s
args = %(accesslog_args)s
kwargs = %(accesslog_kwargs)s
level = %(accesslog_level)s
formatter = message

[handler_eventlog]
class = %(eventlog_handler)s
args = %(eventlog_args)s
kwargs = %(eventlog_kwargs)s
level = NOTSET
formatter = generic

[formatter_generic]
format = %%(asctime)s %%(levelname)-7.7s [%%(name)s:%%(lineno)s][%%(threadName)s] %%(message)s

[formatter_message]
format = %%(message)s
"""  # noqa: E501
