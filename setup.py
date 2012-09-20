from setuptools import setup, find_packages

name = "plone.recipe.zope2instance"
version = '4.2.5'

setup(
    name=name,
    version=version,
    author="Hanno Schlichting",
    author_email="hanno@hannosch.eu",
    description="Buildout recipe for creating a Zope 2 instance",
    long_description=(open('README.rst').read() + '\n' +
        open('CHANGES.txt').read()),
    license="ZPL 2.1",
    keywords="zope2 buildout",
    url='http://pypi.python.org/pypi/plone.recipe.zope2instance',
    classifiers=[
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Buildout",
        "Framework :: Plone",
        "Framework :: Zope2",
    ],
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['plone', 'plone.recipe'],
    install_requires=[
        'zc.buildout',
        'setuptools',
        'mailinglogger',
        'zc.recipe.egg',
        'Zope2 >= 2.12.1',
        'ZODB3 >= 3.9',
    ],
    zip_safe=False,
    entry_points={'zc.buildout': ['default = %s:Recipe' % name]},
)
