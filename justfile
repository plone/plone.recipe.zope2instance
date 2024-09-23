
all_environments := `./.devenv/state/venv/bin/tox list | sed '/default environments:$/d' | sed 's/^\([^ ]*\).*$/\1/' | tr '\n' ','`

# run tox with environments: just tox py38,py39
tox ENVIRONMENTS=all_environments:
	${VIRTUAL_ENV}/bin/tox -e {{ENVIRONMENTS}} -c tox-uv.ini

set positional-arguments

# run zope-testrunner tests; passes args
test *args='': 
	${VIRTUAL_ENV}/bin/zope-testrunner "$@" --path src

