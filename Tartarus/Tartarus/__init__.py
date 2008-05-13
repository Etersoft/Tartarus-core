
__all__ = [ 'iface', 'run1' , 'logging', 'trace_import', 'trace_load']

trace_import = 0
trace_load = 0

import os, sys
module_path = [os.path.join(sys.prefix, 'lib', 'Tartarus', 'modules')]

import iface
iface.setup_import_hook()
iface = iface.Loader()


