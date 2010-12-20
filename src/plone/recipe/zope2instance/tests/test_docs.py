# -*- coding: utf-8 -*-

import doctest
import unittest
import shutil

import pkg_resources
from zc.buildout.testing import buildoutSetUp
from zc.buildout.testing import buildoutTearDown
from zc.buildout.testing import install
from zc.buildout.testing import install_develop


def setUp(test):
    buildoutSetUp(test)
    install_develop('plone.recipe.zope2instance', test)
    install('zc.recipe.egg', test)
    install('mailinglogger', test)
    dependencies = pkg_resources.working_set.require('Zope2')
    for dep in dependencies:
        try:
            install(dep.project_name, test)
        except OSError:
            # Some distributions are installed multiple times, and the
            # underlying API doesn't check for it
            pass


def tearDown(test):
    buildoutTearDown(test)
    sample_buildout = test.globs['sample_buildout']
    shutil.rmtree(sample_buildout, ignore_errors=True)


def test_suite():
    suite = []
    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
        doctest.REPORT_NDIFF)

    suite.append(doctest.DocFileSuite('zope2instance.txt', optionflags=flags,
                 setUp=setUp, tearDown=tearDown))

    return unittest.TestSuite(suite)
