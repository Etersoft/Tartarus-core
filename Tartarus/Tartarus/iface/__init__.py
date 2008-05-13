
import sys
from Tartarus import slices, logging, trace_import

_orig_import = __import__

def tartarus_import(*args):
    logging.trace(__name__,
            "Import hook invoked for name '%s', fromlist = %s"
                % (args[0],args[3]),
            trace_import >= 16)
    name = args[0]
    if name.startswith("Tartarus.iface."):
        if not sys.modules.has_key("name"):
            try:
                # Strip a prefix from argument.
                # len("Tartarus.iface.") == 15
                mname = name[15:]
                slices.load(mname)
            except:
                pass

    elif name == "Tartarus.iface" and len(args) > 3 and args[3] != None:
        # import in form "from Tartarus.iface import ModuleName1, ModuleName2"
        for mname in args[3]:
            try:
                slices.load(mname)
            except:
                pass

    return _orig_import(*args)


def setup_import_hook():
    """Setup hook on __import__.

    This function installs hook on builtin __import__ function,
    which enables autoloading slice files from Tartarus.
    """
    import __builtin__
    __builtin__.__import__ = tartarus_import


class Loader(object):
    """Attributes of this class are submodules of Tartarus.iface package.

    This modules are imported as needed.
    """
    def __getattr__(self, name):
        modname = "Tartarus.iface." + name
        __import__(modname)
        return sys.modules[name]

