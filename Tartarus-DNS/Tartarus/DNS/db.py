

import threading,sys, Tartarus

import Tartarus.iface.DNS as I

_connection = threading.local()

def get_connection():
    try:
        return _connection.val
    except AttributeError:
        _connection.val = _connect()
        return _connection.val



engine='sqlite'
db_opts={}
module = None

_engines_mapping = {
        'sqlite' : 'pysqlite2.dbapi2',
        'sqlite2' : 'pysqlite2.dbapi2',
        'sqlite3' : 'sqlite3'
        }

def _add_to_dict(d,props, key):
    what = props.getProperty("Tartarus.DNS.db."+key)
    if what and len(what) > 0:
        d[key]=what

def _connect():
    return module.connect(**db_opts)

def init(props):
    global engine
    engine = props.getProperty('Tartarus.DNS.db.engine')
    if len(engine) < 1:
        raise I.Errors.ConfigError("Database engine not specified",
                                     "Tartarus.DNS.db.engine")
    e = _engines_mapping[engine]
    __import__(e)
    global module
    module = sys.modules[e]
    for k in ['dsn', 'user', 'password', 'port', 'host', 'database']:
        _add_to_dict(db_opts, props, k)

