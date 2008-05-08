
import sys
from Tartarus import slices

_orig_import = __import__

def import_hook(*args):
    name = args[0]
    if name.startswith("Tartarus.iface."):
        if not sys.modules.has_key("name"):
            try:
                slices.load(name)
            except:
                pass

    return _orig_import(*args)


def setup_import_hook():
    import __builtin__
    __builtin__.__import__ = import_hook


class Loader(object):
    def __getattr__(self, name):
        return __import__("Tartarus.iface." + name)

