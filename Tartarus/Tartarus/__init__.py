
__all__ = [ 'iface', 'run1' ]

import iface

module_path = [os.path.join(sys.prefix, 'lib', 'Tartarus', 'modules')]

iface.setup_import_hook()
iface = iface.Loader()


