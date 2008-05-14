
import sys

class Loader(object):
    """Attributes of this class are submodules of Tartarus.iface package.

    This modules are imported as needed.
    """
    def __getattr__(self, name):
        modname = "Tartarus.iface." + name
        __import__(modname)
        return sys.modules[modname]

