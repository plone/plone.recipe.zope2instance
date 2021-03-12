Please see http://docs.plone.org/develop/coredev/docs/guidelines.html

For development create a Python virtual environment and install one of the both ``requirements-testing-zope*.txt``::

    python3 -m venv .
    bin/pip install -r requirements-testing-zope5.txt
    zope-testrunner --test-path=src
    