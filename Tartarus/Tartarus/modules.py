

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


def load_config(props, cfg_path):
    if len(cfg_path) == 0:
        logging.warning("Tartarus configuration path not specified")
        return
    logging.trace(__name__, "Loading configuration from %s" % cfg_path, trace)
    if not os.path.isdir(cfg_path):
        logging.error("Invalid cfg_path to configuration files: %s" % cfg_path)
        return

    for fi in os.listdir(cfg_path):
        f = os.path.join(cfg_path, fi)
        if not os.path.isfile(f):
            continue
        if not (f.endswith('.conf') or f.endswith('.config')):
            continue
        try:
            props.load(f)
        except Exception:
            logging.error("Failed to load configuration file: %s" % f)


def update_module_path():
    #if no value specified yet, append the default
    global path
    if len(path) == 0:
        p = os.path.join(sys.prefix, 'lib', 'Tartarus', 'modules')
        if os.path.isdir(p):
            path.append(p)
        p = os.path.join(sys.prefix, 'lib64', 'Tartarus', 'modules')
        if os.path.isdir(p):
            path.append(p)

    #update module search path
    for p in path:
        if not os.path.isdir(p):
            logging.warning("Module path not found: %s" % p, trace)
            continue
        if p not in Tartarus.__path__:
            Tartarus.__path__.append(p)


