from setuptools import setup, find_packages

name = "plone.recipe.zope2instance"
version = '3.11'

setup(
    name = name,
    version = version,
    author = "Hanno Schlichting",
    author_email = "hannosch@plone.org",
    description = "ZC Buildout recipe for installing a Zope 2 instance",
    long_description=open('README.txt').read() + '\n' +
                     open('CHANGES.txt').read(),
    license = "ZPL 2.1",
    keywords = "zope2 buildout",
    url='http://pypi.python.org/pypi/plone.recipe.zope2instance',
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Framework :: Plone",
      "Framework :: Zope2",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'': 'src'},
    namespace_packages = ['plone', 'plone.recipe'],
    install_requires = [
        'zc.buildout',
        'setuptools',
        'mailinglogger',
        'zc.recipe.egg',
    ],
    extras_require=dict(
        # zope.testing isn't only a test dependency, but specifying it as a
        # real dependency breaks buildouts in Plone 3 with fake-eggs
        test=['zope.testing'],
    ),
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
