

import os, sys, Tartarus
from Tartarus import logging
path = []

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
    #if no value specified yet, append the default
    global path
    if len(path) == 0:
        path += [os.path.join(sys.prefix, 'lib', 'Tartarus', 'modules')]

    #update module search path
    for p in path:
        if p not in Tartarus.__path__:
            Tartarus.__path__.append(p)

    props = adapter.getCommunicator().getProperties()
    d = props.getPropertiesForPrefix("Tartarus.module.") #note '.' at the end
    if d == {}:
        #load everything we can find
        logging.trace(__name__, "Loading all modules from path.", trace > 16)
        mods = _walk_path(path)
    else:
        mods = d.itervalues()

    for m in mods:
        load_module(m, adapter)


def _walk_path(p):
    for dir in p:
        if not os.path.isdir(dir):
            logging.warning("Directory from Tartarus.modpath not found: %s"
                            % dir)
            continue
        for m in os.listdir(dir):
            if os.path.isdir(os.path.join(dir,m)):
                yield m
            elif trace > 5:
                logging.trace(__name__, "Skipping %s from %s" % (m, dir))

