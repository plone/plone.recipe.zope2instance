# -*- coding: utf-8 -*-
"""
Grabs the doctests in /tests
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import re
import os
import shutil

from zope.testing import renormalizing
import zc.buildout.testing, zc.buildout.easy_install

current_dir = os.path.abspath(os.path.dirname(__file__))
recipe_location = current_dir

for i in range(5):
    recipe_location = os.path.split(recipe_location)[0]


def tearDown(test):
    zc.buildout.testing.buildoutTearDown(test)
    sample_buildout = test.globs['sample_buildout']
    shutil.rmtree(sample_buildout, ignore_errors=True)

def doc_suite(test_dir, globs=None):
    """Returns a test suite, based on doctests found in /doctest."""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE | doctest.REPORT_UDIFF)

    doctest_dir = test_dir

    # filtering files on extension
    docs = [os.path.join(doctest_dir, doc) for doc in
            os.listdir(doctest_dir) if doc.endswith('.txt')]

    for test in docs:
        suite.append(doctest.DocFileSuite(test, optionflags=flags, 
                                          globs=globs, 
                    setUp=zc.buildout.testing.buildoutSetUp,
                    tearDown=tearDown,
                    checker=renormalizing.RENormalizing([
                        zc.buildout.testing.normalize_path,
                        (re.compile(r'\S+buildout.py'), 'buildout.py'),
                        (re.compile(r'line \d+'), 'line NNN'),
                        (re.compile(r'py\(\d+\)'), 'py(NNN)'),
                        ])
                        ,
                      module_relative=False))

    return unittest.TestSuite(suite)

def test_suite():
    """returns the test suite"""
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

