
import threading,sys, Tartarus

import Tartarus.iface.DNS as I
from Ice import ObjectNotExistException as NoSuchObject

engine  = None
db_opts = {}
module  = None

_engines_mapping = {
        'sqlite'        : 'sqlite',
        'sqlite2'       : 'sqlite',
        'postgresql'    : 'psycopg2',
        'postgres'      : 'psycopg2'
        }

def _add_to_dict(d,props, key):
    what = props.getProperty("Tartarus.DNS.db."+key)
    if what and len(what) > 0:
        d[key]=what

#_connection = threading.local()

def get_connection():
    """Get database connection."""
    #try:
    #    return _connection.val
    #except AttributeError:
    #_connection.val = module.connect(**db_opts)
    #return _connection.val
    return module.connect(**db_opts)

def init(props):
    """Initialize internal data."""
    global engine
    if engine is not None:
        raise I.ConfigError("db.init called for second time!", "")
    engine = props.getProperty('Tartarus.DNS.db.engine')
    if len(engine) < 1:
        raise I.ConfigError("Database engine not specified",
                                     "Tartarus.DNS.db.engine")

    try:
        e = _engines_mapping[engine]
    except KeyError:
        raise I.ConfigError("Database engine not supported", engine)

    __import__(e)
    global module
    module = sys.modules[e]
    for k in ['dsn', 'user', 'password', 'port', 'host', 'database']:
        _add_to_dict(db_opts, props, k)

