# -*- coding: utf-8 -*-

import unittest
import doctest
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
    dependencies = pkg_resources.working_set.require('Zope2')
    for dep in dependencies:
        try:
            install(dep.project_name, test)
        except OSError:
            # Some distribution are installed multiple times
            pass


def tearDown(test):
    buildoutTearDown(test)
    sample_buildout = test.globs['sample_buildout']
    shutil.rmtree(sample_buildout, ignore_errors=True)


def test_suite():
    suite = []
    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_UDIFF)

    suite.append(doctest.DocFileSuite('zope2instance.txt',
                 optionflags=flags,
                 setUp=setUp, tearDown=tearDown))

    return unittest.TestSuite(suite)
