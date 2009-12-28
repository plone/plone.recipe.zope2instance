import os
import shutil
import sys

VCS_DIRS = [os.path.normcase("CVS"), os.path.normcase(".svn")]


def make_instance(user=None, instancehome=None):
    instancehome = os.path.abspath(os.path.expanduser(instancehome))
    user, password = user.split(":", 1)

    # Use our own skeleton
    skelsrc = os.path.join(os.path.dirname(__file__), "skel")

    inituser = os.path.join(instancehome, "inituser")
    if not (user or os.path.exists(inituser)):
        user, password = get_inituser()

    copyskel(skelsrc, instancehome)
    if user and password:
        write_inituser(inituser, user, password)


def get_inituser():
    import getpass
    print 'Please choose a username and password for the initial user.'
    print 'These will be the credentials you use to initially manage'
    print 'your new Zope instance.'
    print
    user = raw_input("Username: ").strip()
    if user == '':
        return None, None
    while 1:
        passwd = getpass.getpass("Password: ")
        verify = getpass.getpass("Verify password: ")
        if verify == passwd:
            break
        else:
            passwd = verify = ''
            print "Password mismatch, please try again..."
    return user, passwd


def write_inituser(fn, user, password):
    import binascii
    from hashlib import sha1 as sha
    fp = open(fn, "w")
    pw = binascii.b2a_base64(sha(password).digest())[:-1]
    fp.write('%s:{SHA}%s\n' % (user, pw))
    fp.close()
    os.chmod(fn, 0644)


def copyskel(sourcedir, targetdir):
    # Create the top of the instance:
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

    # This is fairly ugly.  The chdir() makes path manipulation in the
    # walk() callback a little easier (less magical), so we'll live
    # with it.
    pwd = os.getcwd()
    os.chdir(sourcedir)
    try:
        try:
            os.path.walk(os.curdir, copydir, targetdir)
        finally:
            os.chdir(pwd)
    except (IOError, OSError), msg:
        print >>sys.stderr, msg
        sys.exit(1)

    # fix file permissions in 'bin' directory
    bin_dir = os.path.join(targetdir, 'bin')
    for fname in os.listdir(bin_dir):
        fullname = os.path.join(bin_dir, fname)
        os.chmod(fullname, 0700)


def copydir(targetdir, sourcedir, names):
    # Don't recurse into VCS directories:
    for name in names[:]:
        if os.path.normcase(name) in VCS_DIRS:
            names.remove(name)
        elif os.path.isfile(os.path.join(sourcedir, name)):
            # Copy the file:
            sn, ext = os.path.splitext(name)
            if os.path.normcase(ext) == ".in":
                dst = os.path.join(targetdir, sourcedir, sn)
                if os.path.exists(dst):
                    continue
                copyin(os.path.join(sourcedir, name), dst)
            else:
                src = os.path.join(sourcedir, name)
                dst = os.path.join(targetdir, src)
                if os.path.exists(dst):
                    continue
                shutil.copyfile(src, dst)
                shutil.copymode(src, dst)
        else:
            # Directory:
            dn = os.path.join(targetdir, sourcedir, name)
            if not os.path.exists(dn):
                os.mkdir(dn)
                shutil.copymode(os.path.join(sourcedir, name), dn)


def copyin(src, dst):
    ifp = open(src)
    text = ifp.read()
    ifp.close()
    ofp = open(dst, "w")
    ofp.write(text)
    ofp.close()
    shutil.copymode(src, dst)
