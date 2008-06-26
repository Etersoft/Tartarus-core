

import os, sys, Tartarus
from Tartarus import logging
path = []

trace = 0

def load_module(modname, adapter):

    logging.trace(__name__, "Loading module %s." % modname, trace)

    try:
        modname = "Tartarus.%s" % modname
        __import__(modname)
        module = sys.modules[modname]
    except (ImportError, KeyError):
        logging.error("Failed to load module %s, skipping." % modname)
        return
    module.init(adapter)

def _load_config(props, path):
    if not os.path.isdir(path):
        logging.error("Invalid path to configuration files: %s" % path)
        return

    for f in os.listdir(path):
        if not os.path.isfile(f):
            continue
        try:
            props.load(f)
        except:
            logging.error("Failed to load configuration file: %s" % f)


def load_modules1(adapter):
    #if no value specified yet, append the default
    global path
    if len(path) == 0:
        path += [os.path.join(sys.prefix, 'lib', 'Tartarus', 'modules')]

    #update module search path
    for p in path:
        if not os.path.isdir(p):
            logging.trace(__name__, "Module path not found: %s" % p, trace)
            continue
        if p not in Tartarus.__path__:
            Tartarus.__path__.append(p)

    props = adapter.getCommunicator().getProperties()

    conf_dir = props.getPropertyWithDefault(
            "Tartarus.configDir", "/etc/Tartarus")
    _load_config(props, conf_dir)

    d = props.getPropertiesForPrefix("Tartarus.module.") #note '.' at the end

    for m in d.itervalues():
        # we load only modules which names start with big latin letters
        if modname[0] < 'A' or modname[0] > 'Z':
            if trace > 5:
                logging.trace(__name__, "Skipping module %s" % modname)
        else:
            load_module(m, adapter)

