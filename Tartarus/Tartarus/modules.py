

import os, sys, traceback, Tartarus
from Tartarus import logging
path = []

trace = 0

def load_module(modname, adapter):

    logging.trace(__name__, "Loading module %s." % modname, trace)

    modname = "Tartarus.%s" % modname
    try:
        __import__(modname)
        module = sys.modules[modname]
        module.init(adapter)
        return True
    except Exception:
        et, ev, tb = sys.exc_info()
        if et is ImportError and ev.args[0] == modname:
            logging.error("Failed to load module %s, skipping." % modname)
            return False
        if trace <= 16:
            tb = None
        msg = str().join(traceback.format_exception(et, ev, tb))
        logging.error("Failed to load module %s: %s" %
                (modname, msg.strip()))
        return False


def _load_config(props, path):
    if len(path) == 0:
        logging.warning("Tartarus configuration path not specified")
        return
    logging.trace(__name__, "Loading configuration from %s" % path, trace)
    if not os.path.isdir(path):
        logging.error("Invalid path to configuration files: %s" % path)
        return

    for fi in os.listdir(path):
        f = os.path.join(path, fi)
        if not os.path.isfile(f):
            continue
        if not (f.endswith('.conf') or f.endswith('.config')):
            continue
        try:
            props.load(f)
        except:
            logging.error("Failed to load configuration file: %s" % f)


def update_module_path():
    #if no value specified yet, append the default
    global path
    if len(path) == 0:
        path += [os.path.join(sys.prefix, 'lib', 'Tartarus', 'modules')]

    #update module search path
    for p in path:
        if not os.path.isdir(p):
            logging.warning("Module path not found: %s" % p, trace)
            continue
        if p not in Tartarus.__path__:
            Tartarus.__path__.append(p)


