from binascii import b2a_base64
from hashlib import sha1

import os
import os.path
import shutil
import sys


VCS_DIRS = [os.path.normcase("CVS"), os.path.normcase(".svn"), os.path.normcase(".git")]


def make_instance(user=None, instancehome=None, version="4"):
    instancehome = os.path.abspath(os.path.expanduser(instancehome))
    password = None
    if user:
        user, password = user.split(":", 1)

    # Use our own skeleton
    skelsrc = os.path.join(os.path.dirname(__file__), "skel" + version)
    if not os.path.exists(skelsrc):
        raise ValueError(f"No configuration skeleton found for version {version}")

    inituser = os.path.join(instancehome, "inituser")
    if not (user or os.path.exists(inituser)):
        user, password = get_inituser()

    copyskel(skelsrc, instancehome)
    if user and password:
        write_inituser(inituser, user, password)


def get_inituser():
    import getpass

    print(
        """\
Please choose a username and password for the initial user.
These will be the credentials you use to initially manage
your new Zope instance.
"""
    )
    user = input("Username: ").strip()
    if user == "":
        return None, None
    while 1:
        passwd = getpass.getpass("Password: ")
        verify = getpass.getpass("Verify password: ")
        if verify == passwd:
            break
        else:
            passwd = verify = ""
            print("Password mismatch, please try again...")
    return user, passwd


def write_inituser(fn, user, password):
    fp = open(fn, "w")
    pw = b2a_base64(sha1(password.encode("utf-8")).digest())[:-1]
    fp.write("{}:{{SHA}}{}\n".format(user, pw.decode("ascii")))
    fp.close()
    os.chmod(fn, 0o644)


def copyskel(sourcedir, targetdir):
    # Create the top of the instance:
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

    # This is fairly ugly. The chdir() makes path manipulation in the
    # walk() callback a little easier (less magical), so we'll live with it.
    pwd = os.getcwd()
    os.chdir(sourcedir)
    try:
        try:
            copydir(os.curdir, targetdir)
        finally:
            os.chdir(pwd)
    except OSError as msg:
        print(msg, file=sys.stderr)
        sys.exit(1)


def copydir(sourcedir, targetdir):
    for root, dirs, files in os.walk(sourcedir):
        # Don't recurse into VCS directories:
        dirs[:] = set(dirs).difference(VCS_DIRS)
        for name in files:
            src = os.path.join(root, name)
            dst = os.path.join(targetdir, src)
            if os.path.exists(dst):
                continue
            shutil.copyfile(src, dst)
        for name in dirs:
            dn = os.path.join(targetdir, sourcedir, name)
            if not os.path.exists(dn):
                os.mkdir(dn)
