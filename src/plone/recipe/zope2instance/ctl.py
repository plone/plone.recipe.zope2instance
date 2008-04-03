##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""zopectl -- control Zope using zdaemon.

Usage: zopectl [options] [action [arguments]]

Options:
-h/--help -- print usage message and exit
-i/--interactive -- start an interactive shell after executing commands
action [arguments] -- see below

Actions are commands like "start", "stop" and "status". If -i is
specified or no action is specified on the command line, a "shell"
interpreting actions typed interactively is started (unless the
configuration option default_to_interactive is set to false). Use the
action "help" to find out about available actions.
"""

import os, sys
try:
    # Zope 2.8+
    from Zope2.Startup import zopectl
    from Zope2.Startup import handlers
except ImportError:
    # Zope 2.7 (and below)
    from Zope.Startup import zopectl
    from Zope.Startup import handlers    

TESTRUNNER = True
try:
    import zope.testing.testrunner
except ImportError:
    TESTRUNNER = False

WIN32 = False
if sys.platform[:3].lower() == "win":
    WIN32 = True

class AdjustedZopeCmd(zopectl.ZopeCmd):

    if WIN32:
        def get_status(self):
            self.zd_up = 0
            self.zd_pid = 0
            self.zd_status = None
            return

        def do_install(self, arg):
            program = "%s install" % self.options.servicescript
            print program
            os.system(program)

        def do_remove(self, arg):
            program = "%s remove" % self.options.servicescript
            print program
            os.system(program)

        def do_start(self, arg):
            program = "%s start" % self.options.servicescript
            print program
            os.system(program)

        def do_stop(self, arg):
            program = "%s stop" % self.options.servicescript
            print program
            os.system(program)

        def do_restart(self, arg):
            program = "%s restart" % self.options.servicescript
            print program
            os.system(program)

        def get_startup_cmd(self, python, more):
            # if we pass a win32 backslashed path as a ''-style
            # string, the backslashes will act as escapes.
            # Use r'' instead.
            cmdline = ( '%s -c "from Zope2 import configure;'
                        'configure(r\'%s\');' %
                        (python, self.options.configfile)
                        )
            return cmdline + more + '\"'

    def do_console(self, arg):
        self.do_foreground(arg, debug=False)

    def help_console(self):
        print "console -- Run the program in the console."
        print "    In contrast to foreground this does not turn on debug mode."

    def do_foreground(self, arg, debug=True):
        if not WIN32:
            self.get_status()
            pid = self.zd_pid
            if pid:
                print "To run the program in the foreground, please stop it first."
                return
        # Quote the program name, so it works even if it contains spaces
        program = self.options.program
        program[0] = '"%s"' % program[0]
        if debug:
            program[1:1] = ["-X", '"debug-mode=on"']
        program = " ".join(program)
        if WIN32:
            # odd, but true: the windows cmd processor can't handle more than
            # one quoted item per string unless you add quotes around the
            # whole line.
            program = '"%s"' % program
        print program
        try:
            os.system(program)
        except KeyboardInterrupt:
            print

    def do_test(self, arg):
        if not TESTRUNNER:
            # This is probably Zope <= 2.8
            zopectl.ZopeCmd.do_test(self, arg)
            return

        # We overwrite the test command to populate the search path
        # automatically with all configured products and eggs.
        args = filter(None, arg.split(' '))
        defaults = []
        softwarehome = self.options.configroot.softwarehome

        # Put all packages found in products directories on the test-path.
        import Products
        products = []
        for path in Products.__path__:
            # ignore software home, as it already works
            if not path.startswith(softwarehome):
                # get all folders in the current products folder and filter
                # out everything that is not a directory or a VCS internal one.
                folders = [f for f in os.listdir(path) if
                             os.path.isdir(os.path.join(path, f)) and
                             not f.startswith('.') and not f == 'CVS']
                if folders:
                    for folder in folders:
                        # look into all folders and see if they have an
                        # __init__.py in them. This filters out non-packages
                        # like for example documenation folders
                        package = os.path.join(path, folder)
                        if os.path.exists(os.path.join(package, '__init__.py')):
                            products.append(package)

        # Put all packages onto the search path as a package. As we only deal
        # with products, the package name is always prepended by 'Products.'
        for product in products:
            defaults += ['--package-path', product, 'Products.%s' % os.path.split(product)[-1]]

        # Put everything on sys.path into the test-path.
        # XXX This might be too much, but ensures all activated eggs are found.
        # What we really would want here, is to put only the eggs onto the
        # test-path

        # XXX Somehow the buildout root gets on the sys.path. This causes
        # weird problems, as packages like src.plone.portlets.plone.portlets
        # are found by the testrunner
        paths = sys.path
        progname = self.options.progname
        buildout_root = os.path.dirname(os.path.dirname(progname))

        for path in paths:
            if path != buildout_root:
                defaults += ['--test-path', path]

        # Default to dots, if not explicitly set to quiet. Don't duplicate
        # the -v if it is specified manually.
        if '-v' not in args and '-q' not in args:
            defaults.append('-v')

        # Add the --nowarnings option.
        import zope.testing.testrunner

        def filter_warnings(option, opt, *ignored):
            import warnings
            warnings.simplefilter('ignore', Warning, append=True)

        zope.testing.testrunner.other.add_option(
            '--nowarnings', action='callback', callback=filter_warnings,
            help="Install a filter to suppress warnings emitted by code.\n")

        # Run the testrunner. Calling it directly ensures that it is executed
        # in the same environment that we just carefully configured.
        args.insert(0, zope.testing.testrunner.__file__)
        zope.testing.testrunner.run(defaults, args)


def main(args=None):
    # This is mainly a copy of zopectl.py's main function from Zope2.Startup
    options = zopectl.ZopeCtlOptions()
    # Realize arguments and set documentation which is used in the -h option
    options.realize(args, doc=__doc__)
    # We use our own ZopeCmd set, that is derived from the original one.
    c = AdjustedZopeCmd(options)

    # We need to apply a number of hacks to make things work:

    # This puts amongst other things all the configured products directories
    # into the Products.__path__ so we can put those on the test path
    handlers.root_handler(options.configroot)

    # We need to apply the configuration in one more place
    import App.config
    App.config.setConfiguration(options.configroot)

    # The PYTHONPATH is not set, so all commands starting a new shell fail
    # unless we set it explicitly
    os.environ['PYTHONPATH'] = os.path.pathsep.join(sys.path)

    # Add the path to the zopeservice.py script, which is needed for some of the
    # Windows specific commands    
    servicescript = os.path.join(options.configroot.instancehome, 'bin', 'zopeservice.py')
    options.servicescript = '"%s" %s' % (options.python, servicescript)


    # If no command was specified we go into interactive mode.
    if options.args:
        c.onecmd(" ".join(options.args))
    else:
        options.interactive = 1
    if options.interactive:
        try:
            import readline
        except ImportError:
            pass
        print "program:", " ".join(options.program)
        c.do_status()
        c.cmdloop()
