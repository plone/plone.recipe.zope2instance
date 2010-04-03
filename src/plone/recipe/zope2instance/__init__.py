
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

import os
import os.path
import re
import shutil
import sys

import pkg_resources
import zc.buildout
import zc.buildout.easy_install
import zc.recipe.egg

from plone.recipe.zope2instance import make

IS_WIN = sys.platform[:3].lower() == 'win'


class Recipe:

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.buildout, self.options, self.name = buildout, options, name

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['scripts'] = '' # suppress script generation.

        # Relative path support for the generated scripts
        relative_paths = options.get(
            'relative-paths',
            buildout['buildout'].get('relative-paths', 'false')
            )
        if relative_paths == 'true':
            options['buildout-directory'] = buildout['buildout']['directory']
            self._relative_paths = options['buildout-directory']
        else:
            self._relative_paths = ''

    def install(self, update=False):
        options = self.options
        location = options['location']

        if not update:
            if os.path.exists(location):
                shutil.rmtree(location)

            # Which Zope2 version do we have?
            dist = pkg_resources.get_distribution('Zope2')
            parsed = dist.parsed_version
            major, minor = parsed[0:2]
            major, minor = int(major), int(minor)
            # We only support creating instances for 2.12 and 2.13
            if minor > 13:
                minor = 13
            version = str(major) + str(minor)
            make.make_instance(options.get('user', None), location, version)

        try:
            # Make a new zope.conf based on options in buildout.cfg
            self.build_zope_conf()

            # Install extra scripts
            self.install_scripts()

            # Add zcml files to package-includes
            self.build_package_includes()
        except:
            # clean up
            if os.path.exists(location):
                shutil.rmtree(location)
            raise

        return location

    def update(self):
        return self.install(update=True)

    def build_zope_conf(self):
        """Create a zope.conf file
        """

        options = self.options
        location = options['location']
        # Don't do this if we have a manual zope.conf
        zope_conf_path = options.get('zope-conf', None)
        if zope_conf_path is not None:
            return

        products = options.get('products', '')
        if products:
            products = products.split('\n')
            # Filter out empty directories
            products = [p for p in products if p]
            # Make sure we have consistent path seperators
            products = [os.path.abspath(p) for p in products]

        base_dir = self.buildout['buildout']['directory']
        var_dir = options.get('var', os.path.join(base_dir, 'var'))
        if not os.path.exists(var_dir):
            os.makedirs(var_dir)

        instance_home = location
        client_home = options.get('client-home', os.path.join(var_dir,
                                                              self.name))
        if not os.path.exists(client_home):
            os.makedirs(client_home)

        client_import = os.path.join(client_home, 'import')
        if not os.path.exists(client_import):
            os.makedirs(client_import)

        products_lines = '\n'.join(['products %s' % p for p in products])
        module_paths = options.get('extra-paths', '')
        if module_paths:
            module_paths = module_paths.split('\n')
            # Filter out empty directories
            module_paths = [p for p in module_paths if p]
            # Make sure we have consistent path seperators
            module_paths = [os.path.abspath(p) for p in module_paths]
        paths_lines = '\n'.join(['path %s' % p for p in module_paths])
        debug_mode = options.get('debug-mode', 'off')
        security_implementation = 'C'
        verbose_security = options.get('verbose-security', 'off')
        if verbose_security == 'on':
            security_implementation = 'python'
        port_base = options.get('port-base', '')
        if port_base:
            port_base = 'port-base %s' % port_base
        http_address = options.get('http-address', '8080')
        http_fast_listen = options.get('http-fast-listen', None)
        if http_fast_listen is None:
            http_fast_listen = ''
        else:
            http_fast_listen = http_fast_listen_template % http_fast_listen
        ftp_address = options.get('ftp-address', '')
        if ftp_address:
            ftp_address = ftp_server_template % ftp_address
        webdav_address = options.get('webdav-address', '')
        if webdav_address:
            webdav_conn_close = options.get(
                                    'webdav-force-connection-close',
                                    'off')
            webdav_address = webdav_server_template % (webdav_address,
                                                       webdav_conn_close)
        icp_address = options.get('icp-address', '')
        if icp_address:
            icp_address = icp_server_template % icp_address
        effective_user = options.get('effective-user', '')
        if effective_user:
            effective_user = 'effective-user %s' % effective_user
        ip_address = options.get('ip-address', '')
        if ip_address:
            ip_address = 'ip-address %s' % ip_address
        environment_vars = options.get('environment-vars', '')
        if environment_vars:
            # if the vars are all given on one line we need to do some work
            if not '\n' in environment_vars:
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
                environment_vars = '\n'.join(["%s %s" % (env_var[0], env_var[1])
                                             for env_var in env_vars])
            environment_vars = environment_template % environment_vars

        deprecation_warnings = options.get('deprecation-warnings', '')
        if deprecation_warnings:
            if deprecation_warnings.lower() in ('off', 'disable', 'false'):
                deprecation_warnings = 'ignore'
            elif deprecation_warnings.lower() in ('enable', 'on', 'true'):
                deprecation_warnings = 'default'
            deprecation_warnings = '\n'.join((
                "<warnfilter>",
                "  action %s" % deprecation_warnings,
                "  category exceptions.DeprecationWarning",
                "</warnfilter>"))

        zope_conf_additional = options.get('zope-conf-additional', '')

        event_log_level = options.get('event-log-level', 'INFO')
        custom_event_log = options.get('event-log-custom', None)
        default_log = os.path.sep.join(('log', self.name + '.log',))
        # log file
        if custom_event_log is None:
            event_log_name = options.get('event-log', default_log)
            event_file = os.path.join(var_dir, event_log_name)
            event_log_dir = os.path.dirname(event_file)
            if not os.path.exists(event_log_dir):
                os.makedirs(event_log_dir)
            event_log = event_logfile % {'event_logfile': event_file,
                                         'event_log_level': event_log_level}
        # custom log
        else:
            event_log = custom_event_log

        z_log_name = os.path.sep.join(('log', self.name + '-Z2.log'))
        z_log_name = options.get('z2-log', z_log_name)
        z_log = os.path.join(var_dir, z_log_name)
        z_log_dir = os.path.dirname(z_log)
        if not os.path.exists(z_log_dir):
            os.makedirs(z_log_dir)

        z_log_level = options.get('z2-log-level', 'WARN')

        # access event log
        custom_access_event_log = options.get('access-log-custom', None)
        # filelog directive
        if custom_access_event_log is None:
            access_event_log = access_event_logfile % {'z_log': z_log}
        # custom directive
        else:
            access_event_log = custom_access_event_log

        default_zpublisher_encoding = options.get('default-zpublisher-encoding',
                                                  'utf-8')
        if default_zpublisher_encoding:
            default_zpublisher_encoding = 'default-zpublisher-encoding %s' %\
                                          default_zpublisher_encoding

        relstorage = options.get('rel-storage')
        if relstorage:
            def _split(el):
                el = el.split(None, 1)
                return len(el) == 2 and el or None

            rel_storage = dict([
                _split(el) for el in relstorage.splitlines()
                if _split(el) is not None])
            type_ = rel_storage.pop('type', 'postgresql')

            if type_ == 'postgresql' and not 'dsn' in rel_storage:
                # Support zope2instance 1.4 style interpolation for
                # postgresql
                template = ("dbname='%(dbname)s' user='%(user)s' "
                            "host='%(host)s' password='%(password)s'")
                dsn = template % rel_storage
                del rel_storage['dbname']
                del rel_storage['user']
                del rel_storage['host']
                del rel_storage['password']
                rel_storage['dsn'] = dsn

            rel_storage_outer_opts = (
                'name',
                'read-only',
                'blob-dir',
                'keep-history',
                'replica-conf',
                'replica-timeout',
                'poll-interval',
                'pack-gc',
                'pack-dry-run',
                'pack-batch-timeout',
                'pack-duty-cycle',
                'pack-max-delay',
                'cache-servers',
                'cache-module-name',
                'cache-prefix',
                )

            opts = dict(
                type=type_,
                db_opts='\n'.join(' ' * 12 + ' '.join((k, v))
                                  for k, v in rel_storage.iteritems()
                                  if k not in rel_storage_outer_opts),
                rs_opts='\n'.join(' ' * 8 + ' '.join((k, v))
                                  for k, v in rel_storage.iteritems()
                                  if k in rel_storage_outer_opts),
                )
            storage_snippet = rel_storage_template % opts

        else:
            file_storage = options.get('file-storage',
                                       os.path.sep.join(('filestorage',
                                                         'Data.fs',)))
            file_storage = os.path.join(var_dir, file_storage)
            file_storage_dir = os.path.dirname(file_storage)
            if not os.path.exists(file_storage_dir):
                os.makedirs(file_storage_dir)
            storage_snippet = file_storage_template % file_storage
            blob_storage = options.get('blob-storage',
                                       os.path.join(var_dir, 'blobstorage'))

            demo_storage = options.get('demo-storage', 'off') \
                         not in ('off', 'disable', 'false')

            if demo_storage:
                # Disable blob storage when using a demo storage, is that
                # really not support in Zope 2.12?
                blob_storage = None

            if blob_storage:
                blob_storage = os.path.join(base_dir, blob_storage)
                if not os.path.exists(blob_storage):
                    os.makedirs(blob_storage)
                storage_snippet = blob_storage_template % (blob_storage,
                                                           file_storage)

            elif demo_storage:
                storage_snippet = demo_storage_template % storage_snippet

        zserver_threads = options.get('zserver-threads', '2')
        if zserver_threads:
            zserver_threads = 'zserver-threads %s' % zserver_threads

        python_check_interval = options.get('python-check-interval', '1000')
        if python_check_interval:
            python_check_interval = "python-check-interval %s" % python_check_interval

        enable_products = options.get('enable-product-installation', 'off')
        if enable_products:
            enable_products = "enable-product-installation %s" % enable_products

        zeo_client = options.get('zeo-client', '')
        zeo_address = options.get('zeo-address', '8100')

        zodb_cache_size = options.get('zodb-cache-size', '10000')
        if zodb_cache_size:
            zodb_cache_size = "cache-size %s" % zodb_cache_size
        else:
            zodb_cache_size = ""
        zodb_cache_size_bytes = options.get('zodb-cache-size-bytes', None)
        if zodb_cache_size_bytes:
            zodb_cache_size_bytes = "cache-size-bytes %s" % zodb_cache_size_bytes
        else:
            zodb_cache_size_bytes = ""
        zeo_client_cache_size = options.get('zeo-client-cache-size', '128MB')
        zeo_storage = options.get('zeo-storage', '1')

        if zeo_client.lower() in ('yes', 'true', 'on', '1'):
            zeo_client_name = options.get('zeo-client-name', self.name)
            zeo_var_dir = options.get('zeo-var',
                                      os.path.join(instance_home, 'var'))
            zeo_client_client = options.get('zeo-client-client', '')
            zeo_client_min_disconnect_poll = options.get('min-disconnect-poll', "")
            zeo_client_max_disconnect_poll = options.get('max-disconnect-poll', "")
            shared_blob_dir = options.get('shared-blob', 'no')
            if zeo_client_name:
                zeo_client_name = 'zeo-client-name %s' % zeo_client_name
            if zeo_client_client:
                zeo_client_client = 'client %s' % zeo_client_client
            if zeo_client_min_disconnect_poll:
                zeo_client_min_disconnect_poll = "min-disconnect-poll %s" % zeo_client_min_disconnect_poll
            if zeo_client_max_disconnect_poll:
                zeo_client_max_disconnect_poll = "max-disconnect-poll %s" % zeo_client_max_disconnect_poll
            if options.get('zeo-username', ''):
                if not options.get('zeo-password', ''):
                    raise zc.buildout.UserError('No ZEO password specified')

                zeo_authentication = zeo_authentication_template % dict(
                        realm = options.get('zeo-realm', 'ZEO'),
                        username = options.get('zeo-username'),
                        password = options.get('zeo-password'))
            else:
                zeo_authentication = ''

            if blob_storage:
                storage_snippet_template = zeo_blob_storage_template
            elif demo_storage:
                storage_snippet_template = demo_storage_template % zeo_storage_template
            else:
                storage_snippet_template = zeo_storage_template

            storage_snippet = storage_snippet_template % dict(
                blob_storage = blob_storage,
                shared_blob_dir = shared_blob_dir,
                zeo_address = zeo_address,
                zeo_client_cache_size = zeo_client_cache_size,
                zeo_authentication = zeo_authentication,
                zeo_client_client = zeo_client_client,
                zeo_storage = zeo_storage,
                zeo_var_dir=zeo_var_dir,
                zeo_client_min_disconnect_poll=zeo_client_min_disconnect_poll,
                zeo_client_max_disconnect_poll=zeo_client_max_disconnect_poll,
                )
        else:
            # no zeo-client
            zeo_client_client = ''
            zeo_client_name = ''

        zodb_tmp_storage = options.get('zodb-temporary-storage',
                                       zodb_temporary_storage_template)

        template = zope_conf_template

        pid_file = options.get(
            'pid-file',
            os.path.join(var_dir, self.name + '.pid'))
        pid_file_dir = os.path.dirname(pid_file)
        if not os.path.exists(pid_file_dir):
            os.makedirs(pid_file_dir)

        lock_file = options.get(
            'lock-file',
            os.path.join(var_dir, self.name + '.lock'))
        lock_file_dir = os.path.dirname(lock_file)
        if not os.path.exists(lock_file_dir):
            os.makedirs(lock_file_dir)

        zope_conf = template % dict(instance_home = instance_home,
                                    client_home = client_home,
                                    paths_lines = paths_lines,
                                    products_lines = products_lines,
                                    debug_mode = debug_mode,
                                    security_implementation = security_implementation,
                                    verbose_security = verbose_security,
                                    effective_user = effective_user,
                                    ip_address = ip_address,
                                    event_log = event_log,
                                    event_log_level = event_log_level,
                                    access_event_log = access_event_log,
                                    z_log_level = z_log_level,
                                    default_zpublisher_encoding = default_zpublisher_encoding,
                                    storage_snippet = storage_snippet.strip(),
                                    port_base = port_base,
                                    http_address = http_address,
                                    http_fast_listen = http_fast_listen,
                                    ftp_address = ftp_address,
                                    webdav_address = webdav_address,
                                    icp_address = icp_address,
                                    zserver_threads = zserver_threads,
                                    zodb_cache_size = zodb_cache_size,
                                    zodb_cache_size_bytes = zodb_cache_size_bytes,
                                    zeo_client_name = zeo_client_name,
                                    zodb_tmp_storage = zodb_tmp_storage,
                                    pid_file = pid_file,
                                    lock_file = lock_file,
                                    environment_vars = environment_vars,
                                    deprecation_warnings = deprecation_warnings,
                                    python_check_interval = python_check_interval,
                                    enable_products = enable_products,
                                    zope_conf_additional = zope_conf_additional,)

        zope_conf_path = os.path.join(location, 'etc', 'zope.conf')
        try:
            fd = open(zope_conf_path, 'w')
            fd.write(zope_conf)
        finally:
            fd.close()

    def install_scripts(self):
        options = self.options
        location = options['location']

        # The instance control script
        zope_conf = os.path.join(location, 'etc', 'zope.conf')
        zope_conf_path = options.get('zope-conf', zope_conf)

        extra_paths = options.get('extra-paths', '').split()
        requirements, ws = self.egg.working_set(['plone.recipe.zope2instance'])

        zc.buildout.easy_install.scripts(
            [(self.options.get('control-script', self.name),
              'plone.recipe.zope2instance.ctl', 'main')],
            ws, options['executable'], options['bin-directory'],
            extra_paths = extra_paths,
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % zope_conf_path
                         ),
            relative_paths=self._relative_paths,
            )

    def build_package_includes(self):
        """Create ZCML slugs in etc/package-includes
        """
        location = self.options['location']
        sitezcml_path = os.path.join(location, 'etc', 'site.zcml')
        zcml = self.options.get('zcml')
        site_zcml = self.options.get('site-zcml')
        additional_zcml = self.options.get("zcml-additional")

        if site_zcml:
            open(sitezcml_path, 'w').write(site_zcml)
            return

        if zcml:
            zcml = zcml.split()

        if additional_zcml or zcml:
            includes_path = os.path.join(location, 'etc', 'package-includes')

            if not os.path.exists(includes_path):
                # Zope 2.9 does not have a package-includes so we
                # create one.
                os.mkdir(includes_path)
            else:
                if zcml and '*' in zcml:
                    zcml.remove('*')
                else:
                    shutil.rmtree(includes_path)
                    os.mkdir(includes_path)

        if additional_zcml:
            path=os.path.join(includes_path, "999-additional-overrides.zcml")
            open(path, "w").write(additional_zcml.strip())

        if zcml:
            n = 0
            package_match = re.compile('\w+([.]\w+)*$').match
            for package in zcml:
                n += 1
                orig = package
                if ':' in package:
                    package, filename = package.split(':')
                else:
                    filename = None

                if '-' in package:
                    package, suff = package.split('-')
                    if suff not in ('configure', 'meta', 'overrides'):
                        raise ValueError('Invalid zcml', orig)
                else:
                    suff = 'configure'

                if filename is None:
                    filename = suff + '.zcml'

                if not package_match(package):
                    raise ValueError('Invalid zcml', orig)

                path = os.path.join(
                    includes_path,
                    "%3.3d-%s-%s.zcml" % (n, package, suff),
                    )
                open(path, 'w').write(
                    '<include package="%s" file="%s" />\n'
                    % (package, filename)
                    )


# Storage snippets for zope.conf template
file_storage_template="""
    # FileStorage database
    <filestorage>
      path %s
    </filestorage>
"""

demo_storage_template="""
    # Demostorage
    <demostorage>
%s
    </demostorage>
"""

rel_storage_template="""
    %%import relstorage
    <relstorage>
%(rs_opts)s
        <%(type)s>
%(db_opts)s
        </%(type)s>
    </relstorage>
"""

blob_storage_template="""
    # Blob-enabled FileStorage database
    <blobstorage>
      blob-dir %s
      <filestorage>
        path %s
      </filestorage>
    </blobstorage>
"""

zeo_authentication_template="""
    realm %(realm)s
      username %(username)s
      password %(password)s
""".strip()

zeo_storage_template="""
    # ZEOStorage database
    <zeoclient>
      server %(zeo_address)s
      storage %(zeo_storage)s
      name zeostorage
      var %(zeo_var_dir)s
      cache-size %(zeo_client_cache_size)s
      %(zeo_authentication)s
      %(zeo_client_client)s
      %(zeo_client_min_disconnect_poll)s
      %(zeo_client_max_disconnect_poll)s
    </zeoclient>
""".strip()

zeo_blob_storage_template="""
    # Blob-enabled ZEOStorage database
    <zeoclient>
      blob-dir %(blob_storage)s
      shared-blob-dir %(shared_blob_dir)s
      server %(zeo_address)s
      storage %(zeo_storage)s
      name zeostorage
      var %(zeo_var_dir)s
      cache-size %(zeo_client_cache_size)s
      %(zeo_authentication)s
      %(zeo_client_client)s
      %(zeo_client_min_disconnect_poll)s
      %(zeo_client_max_disconnect_poll)s
    </zeoclient>
""".strip()

zodb_temporary_storage_template="""
<zodb_db temporary>
    # Temporary storage database (for sessions)
    <temporarystorage>
      name temporary storage for sessioning
    </temporarystorage>
    mount-point /temp_folder
    container-class Products.TemporaryFolder.TemporaryContainer
</zodb_db>
""".strip()

http_fast_listen_template="""\
  # Set to off to defer opening of the HTTP socket until the end of the
  # startup phase:
  fast-listen %s
""".rstrip()

event_logfile = """
  <logfile>
    path %(event_logfile)s
    level %(event_log_level)s
  </logfile>
""".strip()

access_event_logfile = """
  <logfile>
    path %(z_log)s
    format %%(message)s
  </logfile>
""".strip()

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
  # valid keys are "address" and "force-connection-close"
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
zope_conf_template="""\
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
%(ip_address)s
%(zserver_threads)s
%(zeo_client_name)s
%(environment_vars)s
%(deprecation_warnings)s

<eventlog>
  level %(event_log_level)s
  %(event_log)s
</eventlog>

<logger access>
  level %(z_log_level)s
  %(access_event_log)s
</logger>

<http-server>
  # valid keys are "address" and "force-connection-close"
  address %(http_address)s
%(http_fast_listen)s
</http-server>

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
