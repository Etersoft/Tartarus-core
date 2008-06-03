
import Ice, sys, glob, os, Tartarus

from Tartarus import logging

path = []
trace = 0

_orig_import = __import__

def load(name):
    """Load Tartarus interface.

    Name is in form ModName.SubModName.SubModName ...

    This function finds directory ModName in n Tartarus.slices.path and loads
    all slice files from it in hope that it makes module Tartarus.iface.<name>
    avaliable.
    """
    global path

    # append default path if needed.
    if len(path) == 0:
        path = [os.path.join(sys.prefix, 'share', 'Tartarus', 'slice') ]

    period = name.find(".")
    if period > 0:
        modname = name[:period]
    else:
        modname = name;

    if "Tartarus.iface." + modname in sys.modules:
        return

    logging.trace(__name__, "Loading %s interface" % modname, trace)

    mpath = None
    for dir in path:
        test = os.path.join(dir, modname)
        if os.path.isdir(test):
            mpath = test
            break

    logging.trace(__name__,
            "In path %s found dir %s" % (path, mpath), trace >= 16)

    if mpath is None:
        raise RuntimeError,\
                "Could not find module '%s' in path %s" % (modname, path)

    files = glob.glob(os.path.join(mpath, "*.ice"))
    logging.trace(__name__, "Loading slices: %s" % files, trace >= 16)
    Ice.loadSlice("--all -I%s"  % mpath, [ "-I%s" % d for d in path ] + files)


def tartarus_import(*args):
    """This function is used as import hook in Tartarus."""

    name = args[0]
    if len(args) > 3:
        fromlist = args[3]
    else:
        fromlist = None

    logging.trace(__name__,
            "Import hook invoked for name '%s', fromlist = %s"
                % (name, fromlist),
            trace >= 16)
    if name.startswith("Tartarus.iface."):
        if name not in sys.modules:
            try:
                # Strip a prefix from argument.
                # len("Tartarus.iface.") == 15
                mname = name[15:]
                load(mname)
            except:
                pass

    elif name == "Tartarus.iface" and fromlist is not None:
        # import in form "from Tartarus.iface import ModuleName1, ModuleName2"
        for mname in fromlist:
            try:
                load(mname)
            except:
                pass

    return _orig_import(*args)


def setup_import_hook():
    """Setup hook on __import__.

    This function installs hook on builtin __import__ function,
    which enables autoloading slice files from Tartarus.
    """
    import __builtin__
    _orig_import = __builtin__.__import__
    __builtin__.__import__ = tartarus_import


