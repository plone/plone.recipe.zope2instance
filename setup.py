# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


name = "plone.recipe.zope2instance"
version = '5.0.0'

setup(
    name=name,
    version=version,
    author="Hanno Schlichting",
    author_email="hanno@hannosch.eu",
    description="Buildout recipe for creating a Zope 2 instance",
    long_description=((open('README.rst').read() + '\n' +
                       open('CHANGES.rst').read())),
    license="ZPL 2.1",
    keywords="zope2 buildout",
    url='https://pypi.python.org/pypi/plone.recipe.zope2instance',
    classifiers=[
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Buildout",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Zope :: 4",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
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
    ],
    zip_safe=False,
    entry_points={'zc.buildout': ['default = %s:Recipe' % name]},
)
