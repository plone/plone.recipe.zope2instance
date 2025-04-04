from setuptools import find_packages
from setuptools import setup


name = "plone.recipe.zope2instance"
version = "8.0.1"

setup(
    name=name,
    version=version,
    maintainer="Plone Release Team",
    maintainer_email="releaseteam@plone.org",
    author="Hanno Schlichting",
    author_email="hanno@hannosch.eu",
    description="Buildout recipe for creating a Zope instance",
    long_description=(open("README.rst").read() + "\n" + open("CHANGES.rst").read()),
    license="ZPL 2.1",
    keywords="zope buildout",
    url="https://github.com/plone/plone.recipe.zope2instance",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Framework :: Buildout",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=find_packages("src"),
    include_package_data=True,
    package_dir={"": "src"},
    namespace_packages=["plone", "plone.recipe"],
    python_requires=">=3.9",
    install_requires=[
        "zc.buildout",
        "setuptools",
        "zc.recipe.egg",
        "Zope >= 5.0",
        "ZODB >= 5.1.1",
        "ZEO",
        "waitress >= 1.2.0",
        "Paste",
        "python-dotenv",
    ],
    extras_require={
        "test": [
            "zope.testrunner",
            "sentry-sdk",
        ],
        "sentry": [
            "sentry-sdk",
        ],
        "profile": [
            "repoze.profile",
        ],
    },
    zip_safe=False,
    entry_points={
        "zc.buildout": ["default = %s.recipe:Recipe" % name],
        "paste.server_runner": [
            "main=plone.recipe.zope2instance.ctl:serve_paste",
        ],
        "paste.server_factory": [
            "main=plone.recipe.zope2instance.ctl:server_factory",
        ],
        "paste.filter_factory": [
            "sentry=plone.recipe.zope2instance.sentry:sdk_init",
        ],
    },
)
