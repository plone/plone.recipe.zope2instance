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

import os, sys, csv

from Zope2.Startup import zopectl
from Zope2.Startup import handlers

WIN32 = False
if sys.platform[:3].lower() == "win":
    import pywintypes
    import win32service
    import win32serviceutil

    WIN32 = True

def _n(path):
    return os.path.abspath(os.path.normpath(path)).lower()

def quote_command(command):
    print " ".join(command)
    # Quote the program name, so it works even if it contains spaces
    command = " ".join(['"%s"' % x for x in command])
    if WIN32:
        # odd, but true: the windows cmd processor can't handle more than
        # one quoted item per string unless you add quotes around the
        # whole line.
        command = '"%s"' % command
    return command

class AdjustedZopeCmd(zopectl.ZopeCmd):

    if WIN32:
        def get_status(self):
            sn = self.get_service_name()
            try:
                stat = win32serviceutil.QueryServiceStatus(sn)[1]
                self.zd_up = 1
            except pywintypes.error, err:
                if err[0] == 1060:
                    # Service not installed
                    stat = win32service.SERVICE_STOPPED
                    self.zd_up = 0
                else:
                    raise

            self.zd_pid = (stat == win32service.SERVICE_RUNNING) and -1 or 0
            self.zd_status = "args=%s" % self.options.program

        def get_service_name(self):
            ih = self.options.configroot.instancehome.lower()
            return "Zope_%s" % hash(ih)

        def handle_command(self, cmd):
            # Make a copy of the environment and the sys path so we
            # can restore them afterwards.
            old_env = os.environ.data.copy()
            old_path = sys.path[:]

            try:
                # Make the zopeservice module importable
                parent = os.path.dirname(self.options.servicescript[-1])
                sys.path.insert(0, parent)

                # Import the InstanceService class, and then delegate the
                # commands to HandleCommandLine
                from zopeservice import InstanceService

                serviceClassString = ('%s.%s' % (
                        os.path.join(parent, 'zopeservice'),
                        InstanceService.__name__))
                win32serviceutil.HandleCommandLine(InstanceService,
                                                   serviceClassString,
                                                   argv=['', cmd])
            finally:
                os.environ.data = old_env
                sys.path = old_path

        def do_install(self, arg):
            self.handle_command('install')

        def do_remove(self, arg):
            self.handle_command('remove')

        def do_start(self, arg):
            self.get_status()
            if not self.zd_pid:
                self.handle_command('start')

        def do_stop(self, arg):
            self.get_status()
            if self.zd_pid:
                self.handle_command('stop')

        def do_restart(self, arg):
            self.handle_command('restart')

    def get_startup_cmd(self, python, more, pyflags=""):
        # If we pass the configuration filename as a win32
        # backslashed path using a ''-style string, the backslashes
        # will act as escapes.  Use r'' instead.
        # Also, don't forget that 'python'
        # may have spaces and needs to be quoted.
        cmdline = ( '"%s" %s -c "from Zope2 import configure; '
                    'configure(r\'%s\'); ' %
                    (python, pyflags, self.options.configfile)
                    )
        cmdline = cmdline + more + '\"'
        if WIN32:
            # entire command line must be quoted
            # as well as the components
            return '"%s"' % cmdline
        else:
            return cmdline

    def do_run(self, arg):
        # If the command line was something like
        # """bin/instance run "one two" three"""
        # cmd.parseline will have converted it so
        # that arg == 'one two three'. This is going to
        # foul up any quoted command with embedded spaces.
        # So we have to return to self.options.args,
        # which is a tuple of command line args,
        # throwing away the "run" command at the beginning.
        #
        # Further complications: if self.options.args has come
        # via subprocess, it may look like
        # ['run "arg 1" "arg2"'] rather than ['run','arg 1','arg2'].
        # If that's the case, we'll use csv to do the parsing
        # so that we can split on spaces while respecting quotes.
        if len(self.options.args) == 1:
            tup = csv.reader(self.options.args, delimiter=' ').next()[1:]
        else:
            tup = self.options.args[1:]


        if not tup:
            print "usage: run <script> [args]"
            return

        # If we pass the script filename as a win32 backslashed path
        # using a ''-style string, the backslashes will act as
        # escapes.  Use r'' instead.
        #
        # Remove -c and add script as sys.argv[0]
        script = tup[0]
        cmd = 'import sys; sys.argv.pop(); sys.argv.append(r\'%s\'); '  % script
        if len(tup) > 1:
            argv = tup[1:]
            cmd += '[sys.argv.append(x) for x in %s]; ' % argv
        cmd += 'import Zope2; app=Zope2.app(); execfile(r\'%s\')' % script
        cmdline = self.get_startup_cmd(self.options.python, cmd)
        self._exitstatus = os.system(cmdline)

    def do_console(self, arg):
        self.do_foreground(arg, debug=False)

    def help_console(self):
        print "console -- Run the program in the console."
        print "    In contrast to foreground this does not turn on debug mode."

    def do_debug(self, arg):
        cmdline = self.get_startup_cmd(self.options.python,
                                       'import Zope2; app=Zope2.app()',
                                       pyflags = '-i',)
        print ('Starting debugger (the name "app" is bound to the top-level '
               'Zope object)')
        os.system(cmdline)

    def do_foreground(self, arg, debug=True):
        if not WIN32:
            self.get_status()
            pid = self.zd_pid
            if pid:
                print "To run the program in the foreground, please stop it first."
                return
        program = self.options.program
        if debug:
            local_additions = []
            if not program.count('-X'):
                local_additions += ['-X']
            if not program.count('debug-mode=on'):
                local_additions += ['debug-mode=on']
            program[1:1] = local_additions
            command = quote_command(program)
            try:
                return os.system(command)
            finally:
                for addition in local_additions: program.remove(addition)
        else:
            os.execv(program[0], program)

    def do_test(self, arg):
        print("The test command is no longer supported. Please use a "
              "zc.recipe.testrunner section in your buildout config file "
              "to get a test runner for your environment. Most often you "
              "will name the section `test` and can run tests via: "
              "bin/test -s <my.package>")
        return


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
    servicescript = os.path.join(options.configroot.instancehome,
                                 'bin', 'zopeservice.py')
    options.servicescript = [options.python, servicescript]

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


class NoShellZopeCmd(AdjustedZopeCmd):

    def environment(self):
        configroot = self.options.configroot
        env = dict(os.environ)
        env.update({'SOFTWARE_HOME': configroot.softwarehome,
                    'INSTANCE_HOME': configroot.instancehome,
                    'PYTHONPATH': ':'.join(sys.path + [
                        configroot.softwarehome])})
        return env

    def do_foreground(self, arg, debug=True):
        if not WIN32:
            self.get_status()
            pid = self.zd_pid
            if pid:
                print "To run the program in the foreground, please stop it first."
                return

        import subprocess
        options = self.options
        env = self.environment()
        cmd = self.options.program
        if debug:
            cmd.extend(['-X', 'debug-mode=on'])
            return subprocess.call(cmd, env=env)
        os.execve(cmd[0], cmd, env)

    def do_start(self, arg):
        self.get_status()
        if not self.zd_up:
            args = [
                self.options.python,
                self.options.zdrun,
                ]
            args += self._get_override("-S", "schemafile")
            args += self._get_override("-C", "configfile")
            args += self._get_override("-b", "backofflimit")
            args += self._get_override("-d", "daemon", flag=1)
            args += self._get_override("-f", "forever", flag=1)
            args += self._get_override("-s", "sockname")
            args += self._get_override("-u", "user")
            if self.options.umask:
                args += self._get_override("-m", "umask",
                                           oct(self.options.umask))
            args += self._get_override(
                "-x", "exitcodes", ",".join(map(str, self.options.exitcodes)))
            args += self._get_override("-z", "directory")

            args.extend(self.options.program)

            if self.options.daemon:
                flag = os.P_NOWAIT
            else:
                flag = os.P_WAIT
            os.spawnvpe(flag, args[0], args, self.environment())
        elif not self.zd_pid:
            self.send_action("start")
        else:
            print "daemon process already running; pid=%d" % self.zd_pid
            return
        self.awhile(lambda: self.zd_pid,
                    "daemon process started, pid=%(zd_pid)d")

def noshell(args=None):
    # This is a customized entry point for launching Zope without forking shell
    # scripts or other processes.
    options = zopectl.ZopeCtlOptions()
    # Realize arguments and set documentation which is used in the -h option
    options.realize(args, doc=__doc__)

    # Change the program to avoid warning messages
    script = os.path.join(
        options.configroot.softwarehome, 'Zope2', 'Startup', 'run.py')
    options.program =  [options.python, script, '-C', options.configfile]

    # We use our own ZopeCmd set, that is derived from the original one.
    c = NoShellZopeCmd(options)
    # We need to apply a number of hacks to make things work:

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
    servicescript = os.path.join(options.configroot.instancehome,
                                 'bin', 'zopeservice.py')
    options.servicescript = [options.python, servicescript]

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
