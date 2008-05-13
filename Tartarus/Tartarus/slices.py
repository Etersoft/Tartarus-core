
import Ice, sys, glob, os, Tartarus

from Tartarus import logging



path = [ os.path.join(sys.prefix, 'share', 'Tartarus', 'slice') ]

def load(name):
    """Load Tartarus interface.

    Name is in form ModName.SubModName.SubModName ...

    This function finds directory ModName in n Tartarus.slices.path and loads
    all slice files from it in hope that it makes module Tartarus.iface.<name>
    avaliable.
    """
    logging.trace(__name__, "Loading module %s" % name, Tartarus.trace_import)

    period = name.find(".")
    if period > 0:
        modname = name[:period]
    else:
        modname = name;

    mpath = None
    for dir in path:
        test = os.path.join(dir, modname)
        if os.path.isdir(test):
            mpath = test
            break

    logging.trace(__name__, "In path %s found dir %s" % (path, mpath),
            Tartarus.trace_import >= 16)

    if mpath is None:
        raise RuntimeError, "Could not find module '%s' in path %s" % (modname, path)

    files = glob.glob(os.path.join(mpath, "*.ice"))
    logging.trace(__name__, "Loading slices: %s" % files, Tartarus.trace_import >= 16)
    Ice.loadSlice("--all -I%s"  % mpath, [ "-I%s" % d for d in path ] + files)

