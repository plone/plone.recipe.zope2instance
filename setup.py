from setuptools import setup, find_packages

name = "plone.recipe.zope2instance"
version = '4.0b1'

def read(name):
    return open(name).read()

long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
    )

setup(
    name = name,
    version = version,
    author = "Hanno Schlichting",
    author_email = "hannosch@plone.org",
    description = "ZC Buildout recipe for installing a Zope 2 instance",
    long_description=long_description,
    license = "ZPL 2.1",
    keywords = "zope2 buildout",
    url='http://pypi.python.org/pypi/plone.recipe.zope2instance',
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Framework :: Plone",
      "Framework :: Zope2",
      ],
    tests_require=['zope.testing'],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['plone', 'plone.recipe'],
    install_requires = [
        'zc.buildout',
        'setuptools',
        'zc.recipe.egg',
        'Zope2 >= 2.12.1',
    ],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
