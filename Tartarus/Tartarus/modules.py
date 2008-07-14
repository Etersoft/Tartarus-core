

import os, sys, traceback, Tartarus
from Tartarus import logging
path = []

trace = 0

def load_module(modname, adapter):

    logging.trace(__name__, "Loading module %s." % modname, trace)

    try:
        modname = "Tartarus.%s" % modname
        __import__(modname)
        module = sys.modules[modname]
        module.init(adapter)
        return True
    except (ImportError, KeyError):
        logging.error("Failed to load module %s, skipping." % modname)
        return False
    except Exception:
        et, ev, tb = sys.exc_info()
        if trace <= 16:
            tb = None
        msg = str().join(traceback.format_exception(et, ev, tb))
        logging.error("Failed to load module %s:\n%s" %
                (modname, msg))
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
        if not (f.endwith('.conf') or f.endswith('.config')):
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
            logging.warning("Module path not found: %s" % p, trace)
            continue
        if p not in Tartarus.__path__:
            Tartarus.__path__.append(p)

    props = adapter.getCommunicator().getProperties()

    conf_dir = props.getProperty("Tartarus.configDir")
    _load_config(props, conf_dir)

    d = props.getPropertiesForPrefix("Tartarus.module.") #note '.' at the end
    a = props.getPropertyAsInt("Tartarus.modules.LoadAll")

    for m in d.itervalues():
        # we load only modules which names start with big latin letters
        if m[0] < 'A' or m[0] > 'Z':
            if trace > 5:
                logging.warning("Skipping module %s" % m)
        else:
            res = load_module(m, adapter)
            if not res and a > 0:
                raise RuntimeError("Modules initialization failed")



