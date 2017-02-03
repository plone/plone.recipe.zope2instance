def waitress_main(args=None):
    from paste.deploy import loadserver
    from waitress import serve
    from Zope2.Startup.run import make_wsgi_app
    import pdb; pdb.set_trace()
    wsgiapp = make_wsgi_app(
        {'debug_mode': 'on'},
        '/home/vagrant/plone5devel/parts/wsgi-instance/etc/zope.conf')
    serve(wsgiapp, listen='*:8080')
