
import Ice, sys, logging, glob, os


path = [ os.path.join(sys.prefix, 'share', 'Tartarus', 'slice') ]

def load(name):
    """Load Tartarus interface.

    The argument must be a module name in form 'Tartarus.iface.ModName'
    """
    logging.info("Loading module %s" % name)
    modname = name[len('Tartarus.iface.'):]

    if '.' in modname:
        raise RuntimeError, "Invalid module name: %s" % modname

    mpath = ""
    for dir in path:
        test = os.path.join(dir, modname)
        if os.path.isdir(test):
            mpath = test
            break

    if mpath == "":
        raise RuntimeError, "Slice files not found in slices.path %s" % path

    files = glob.glob(os.path.join(path, "*.ice"))
    Ice.loadSlice("--all -I%s -I%s" %(path, mpath), files)




