from paste.deploy.loadwsgi import APP
from paste.deploy.loadwsgi import ConfigLoader
from paste.deploy.loadwsgi import SERVER
from Zope2.Startup.run import make_wsgi_app


def waitress_main(args=None):
    """
    Configure + start Plone behind waitress from the given PasteDeploy
    configuration
    Waitress - unlike uwsgi - expects us to do the
    PasteDeploy stuff on our own.
    """
    ini_filename = args[-1]
    config_loader = ConfigLoader(ini_filename)
    server_config = config_loader.get_context(SERVER)
    serve = server_config.create()
    app_config = config_loader.get_context(APP)
    zope_conf = app_config.local_conf['zope_conf']
    wsgiapp = make_wsgi_app(app_config.global_conf, zope_conf)
    serve(wsgiapp)
