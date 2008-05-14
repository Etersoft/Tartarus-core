
__all__ = [ 'iface', 'run1' , 'logging', 'slices', 'modules' ]

import iface, slices, modules, logging

slices.setup_import_hook()

iface = iface.Loader()

