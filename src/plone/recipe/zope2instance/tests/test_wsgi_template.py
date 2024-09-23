from os.path import join
from plone.recipe.zope2instance.tests.test_docs import install_dependencies

import os
import pkg_resources
import shutil
import unittest
import zc.buildout.testing as buildout_testing


class WSGITemplateTestCase(unittest.TestCase):

    def setUp(self):
        self.globs = {}
        buildout_testing.buildoutSetUp(self)
        buildout_testing.install_develop("plone.recipe.zope2instance", self)
        buildout_testing.install("zc.recipe.egg", self)
        install_dependencies(pkg_resources.working_set.require("ZEO"), self)
        install_dependencies(pkg_resources.working_set.require("Zope"), self)
        install_dependencies(pkg_resources.working_set.require("ZODB"), self)

    def tearDown(self):
        buildout_testing.buildoutTearDown(self)
        sample_buildout = self.globs["sample_buildout"]
        shutil.rmtree(sample_buildout, ignore_errors=True)

    def test_two_instances(self):
        BUILDOUT_CONTENT = """
[buildout]
parts = instance instance2
find-links = %(sample_buildout)s/eggs

[instance]
recipe = plone.recipe.zope2instance
eggs =
user = me:me

[instance2]
recipe = plone.recipe.zope2instance
eggs =
user = me:me
"""
        buildout_testing.write("buildout.cfg", BUILDOUT_CONTENT % self.globs)
        output = buildout_testing.system(join("bin", "buildout"), with_exit_code=True)
        self.assertTrue("EXIT CODE: 0" in output, output)

    def test_wsgi_ini_template(self):
        BUILDOUT_CONTENT = """
[buildout]
parts = instance
find-links = %(sample_buildout)s/eggs

[instance]
recipe = plone.recipe.zope2instance
eggs =
user = me:me
wsgi-ini-template = %(sample_buildout)s/wsgi_tmpl.ini
"""
        TEMPLATE_CONTENT = """
[section]
bla=BLA
"""
        buildout_testing.write("buildout.cfg", BUILDOUT_CONTENT % self.globs)
        buildout_testing.write("wsgi_tmpl.ini", TEMPLATE_CONTENT)
        output = buildout_testing.system(join("bin", "buildout"))
        self.assertTrue("Installing instance" in output)
        sample_buildout = self.globs["sample_buildout"]
        instance = os.path.join(sample_buildout, "parts", "instance")
        with open(os.path.join(instance, "etc", "wsgi.ini")) as fd:
            wsgi_ini = fd.read()
        self.assertEqual(wsgi_ini, TEMPLATE_CONTENT)

    def test_wsgi_ini_template_and_wsgi_logging_ini_template(self):
        BUILDOUT_CONTENT = """
[buildout]
parts = instance
find-links = %(sample_buildout)s/eggs

[instance]
recipe = plone.recipe.zope2instance
eggs =
user = me:me
wsgi-ini-template = %(sample_buildout)s/wsgi_tmpl.ini
wsgi-logging-ini-template = %(sample_buildout)s/wsgi_tmpl.ini
"""
        TEMPLATE_CONTENT = """
[section]
bla=BLA
"""
        buildout_testing.write("buildout.cfg", BUILDOUT_CONTENT % self.globs)
        buildout_testing.write("wsgi_tmpl.ini", TEMPLATE_CONTENT)
        output = buildout_testing.system(join("bin", "buildout"))
        self.assertTrue("Installing instance" in output)
        self.assertTrue(
            "ValueError: wsgi_ini_template_path and "
            "wsgi_logging_ini_template_path cannot be used together." in output
        )

    def test_wsgi_logging_ini_template(self):
        BUILDOUT_CONTENT = """
[buildout]
parts = instance
find-links = %(sample_buildout)s/eggs

[instance]
recipe = plone.recipe.zope2instance
eggs =
user = me:me
wsgi-logging-ini-template = %(sample_buildout)s/wsgi_logging_tmpl.ini
"""
        TEMPLATE_CONTENT = """
[section]
bla=BLA
"""
        buildout_testing.write("buildout.cfg", BUILDOUT_CONTENT % self.globs)
        buildout_testing.write("wsgi_logging_tmpl.ini", TEMPLATE_CONTENT)
        output = buildout_testing.system(join("bin", "buildout"))
        self.assertTrue("Installing instance" in output)
        sample_buildout = self.globs["sample_buildout"]
        instance = os.path.join(sample_buildout, "parts", "instance")
        with open(os.path.join(instance, "etc", "wsgi.ini")) as fd:
            wsgi_ini = fd.read()
        self.assertTrue(TEMPLATE_CONTENT in wsgi_ini)
