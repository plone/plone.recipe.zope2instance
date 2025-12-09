from setuptools import setup


name = "plone.recipe.zope2instance"
version = "9.0.0a1"

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
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "zc.buildout",
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
            "zope.testrunner >= 6.4",
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
