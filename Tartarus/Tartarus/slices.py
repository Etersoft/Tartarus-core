
import Ice, sys, logging, glob, os


path = [ os.path.join(sys.prefix, 'share', 'Tartarus', 'slice') ]

def load(name):
    """Load Tartarus interface.

    The argument must be a module name in form 'Tartarus.iface.ModName'
    """
    logging.info("Loading module %s" % name)

    period = name.find(".")
    if period > 0:
        modname = name[:period]
    else:
        modname = name;

    mpath = ""
    for dir in path:
        test = os.path.join(dir, modname)
        if os.path.isdir(test):
            mpath = test
            break

    if mpath == "":
        raise RuntimeError, "Could not find module '%s' in path %s" % (modname, path)

    files = glob.glob(os.path.join(path, "*.ice"))
    Ice.loadSlice("--all -I%s -I%s" %(path, mpath), files)




