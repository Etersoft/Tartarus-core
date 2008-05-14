

import os, sys, Tartarus
from Tartarus import logging
path = [os.path.join(sys.prefix, 'lib', 'Tartarus', 'modules')]

trace = 0

def load_module(modname, adapter):
    # we load only modules which names start with big latin letters
    if modname[0] < 'A' or modname[0] > 'Z':
        if trace > 5:
            logging.trace(__name__, "Skipping module %s" % modname)
        return

    logging.trace(__name__, "Loading module %s." % modname, trace)
    modname = "Tartarus.%s" % modname
    __import__(modname)
    module = sys.modules[modname]
    module.init(adapter)

def load_modules1(adapter):
    Tartarus.__path__ += path

    for dir in path:
        if not os.path.isdir(dir):
            logging.warning("Directory from Tartarus.modpath not found: %s"
                            % dir)
            continue
        for m in os.listdir(dir):
            if os.path.isdir(os.path.join(dir,m)):
                    load_module(m, adapter)
            elif trace > 5:
                logging.trace(__name__, "Skipping %s from %s" % (m, dir))

