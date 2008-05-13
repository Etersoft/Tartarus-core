
__all__ = [ 'iface', 'run1' ]


import os, sys
module_path = [os.path.join(sys.prefix, 'lib', 'Tartarus', 'modules')]

import iface
iface.setup_import_hook()
iface = iface.Loader()


