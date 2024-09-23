default_all_environments := `./.devenv/state/venv/bin/tox list | sed '/default environments:$/d' | sed 's/^\([^ ]*\).*$/\1/' | tr '\n' ','`

tox ENVIRONMENT=default_all_environments:
	${VIRTUAL_ENV}/bin/tox -e {{ENVIRONMENT}} -c tox-uv.ini

default_config := ''

test CONFIG=default_config: 
	${VIRTUAL_ENV}/bin/zope-testrunner {{CONFIG}} --path src

