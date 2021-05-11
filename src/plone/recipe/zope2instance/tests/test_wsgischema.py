##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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

from plone.recipe.zope2instance.ctl import WSGICtlOptions

import os
import tempfile
import unittest
import ZConfig


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

_SCHEMA = None
TEMPNAME = tempfile.mktemp()
TEMPVAR = os.path.join(TEMPNAME, "var")


def getSchema():
    global _SCHEMA
    if not _SCHEMA:
        opts = WSGICtlOptions()
        opts.load_schema()
        _SCHEMA = opts.schema
    return _SCHEMA


class StartupTestCase(unittest.TestCase):
    @property
    def schema(self):
        return getSchema()

    def load_config_text(self, text):
        # We have to create a directory of our own since the existence
        # of the directory is checked.  This handles this in a
        # platform-independent way.
        schema = self.schema
        sio = StringIO(text.replace("<<INSTANCE_HOME>>", TEMPNAME))
        os.mkdir(TEMPNAME)
        os.mkdir(TEMPVAR)
        try:
            conf, handler = ZConfig.loadConfigFile(schema, sio)
        finally:
            os.rmdir(TEMPVAR)
            os.rmdir(TEMPNAME)
        self.assertEqual(conf.instancehome, TEMPNAME)
        return conf, handler

    def test_load_config_template(self):
        import Zope2.utilities

        base = os.path.dirname(Zope2.utilities.__file__)
        fn = os.path.join(base, "skel", "etc", "zope.conf.in")
        f = open(fn)
        text = f.read()
        f.close()
        self.load_config_text(text)

    def test_environment(self):
        conf, handler = self.load_config_text(
            """\
            # instancehome is here since it's required
            instancehome <<INSTANCE_HOME>>
            <environment>
              FEARFACTORY rocks
              NSYNC doesnt
            </environment>
            """
        )
        items = list(conf.environment.items())
        items.sort()
        self.assertEqual(items, [("FEARFACTORY", "rocks"), ("NSYNC", "doesnt")])

    def test_zodb_db(self):
        conf, handler = self.load_config_text(
            """\
            instancehome <<INSTANCE_HOME>>
            <zodb_db main>
              <filestorage>
               path <<INSTANCE_HOME>>/var/Data.fs
               </filestorage>
                mount-point /
                cache-size 5000
                pool-size 7
            </zodb_db>
            """
        )
        self.assertEqual(conf.databases[0].config.cache_size, 5000)

    def test_max_conflict_retries_default(self):
        conf, handler = self.load_config_text(
            """\
            instancehome <<INSTANCE_HOME>>
            """
        )
        self.assertEqual(conf.max_conflict_retries, 3)

    def test_max_conflict_retries_explicit(self):
        conf, handler = self.load_config_text(
            """\
            instancehome <<INSTANCE_HOME>>
            max-conflict-retries 15
            """
        )
        self.assertEqual(conf.max_conflict_retries, 15)

    def test_debug_exceptions_default(self):
        conf, handler = self.load_config_text(
            """\
        instancehome <<INSTANCE_HOME>>
        """
        )
        self.assertFalse(conf.debug_exceptions)

    def test_debug_exceptions_explicit(self):
        conf, handler = self.load_config_text(
            """\
        instancehome <<INSTANCE_HOME>>
        debug-exceptions on
        """
        )
        self.assertTrue(conf.debug_exceptions)

    def test_default_zpublisher_encoding(self):
        conf, dummy = self.load_config_text(
            """\
            instancehome <<INSTANCE_HOME>>
            """
        )
        self.assertEqual(conf.default_zpublisher_encoding, "utf-8")

        conf, dummy = self.load_config_text(
            """\
            instancehome <<INSTANCE_HOME>>
            default-zpublisher-encoding iso-8859-15
            """
        )
        self.assertEqual(conf.default_zpublisher_encoding, "iso-8859-15")
