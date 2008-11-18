import os

def main(args=None):
    """ Start a Zope instance """
    import Zope2.Startup

    if args is None:
        return

    configfile = args[0]

    starter = Zope2.Startup.get_starter()
    opts = Zope2.Startup.run._setconfig(configfile=configfile)
    starter.setConfiguration(opts.configroot)
    starter.prepare()
    starter.run()
