# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


name = "plone.recipe.zope2instance"
version = '6.7.2'

setup(
    name=name,
    version=version,
    author="Hanno Schlichting",
    author_email="hanno@hannosch.eu",
    description="Buildout recipe for creating a Zope instance",
    long_description=((open('README.rst').read() + '\n' +
                       open('CHANGES.rst').read())),
    license="ZPL 2.1",
    keywords="zope buildout",
    url='https://github.com/plone/plone.recipe.zope2instance',
    classifiers=[
        "Development Status :: 6 - Mature",
        "Framework :: Buildout",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 4",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['plone', 'plone.recipe'],
    install_requires=[
        'zc.buildout',
        'setuptools',
        'six',
        'zc.recipe.egg',
        'Zope >= 4.0b1',
        'ZODB >= 5.1.1',
        'ZEO',
        'waitress >= 1.2.0',
        'Paste',
    ],
    extras_require={
        'test': [
            'zope.testrunner',
        ],
        'sentry': [
            'sentry-sdk',
        ]
    },
    zip_safe=False,
    entry_points={
        'zc.buildout': ['default = %s.recipe:Recipe' % name],
        'paste.server_runner': [
            'main=plone.recipe.zope2instance.ctl:serve_paste',
        ],
        'paste.server_factory': [
            'main=plone.recipe.zope2instance.ctl:server_factory',
        ],
        'paste.filter_factory': [
            'sentry=plone.recipe.zope2instance.sentry:sdk_init',
        ],
        },
)
