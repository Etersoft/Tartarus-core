"""Tartarus helpers for database.

Many modules of Tartarus work with relational databases. They usualy don't need
ORM, but need a clean, easy and portable way to execute simple SQL queries.

This module is a result of attempt to extract and improve common database code
from such modules.
"""

import sys
from Tartarus import logging

def _engine2module(engine):
    _engines_mapping = {
            'sqlite'        : 'sqlite',
            'sqlite2'       : 'sqlite',
            'sqlite3'       : 'sqlite3',
            'postgresql'    : 'psycopg2',
            'postgres'      : 'psycopg2'
            }
    return _engines_mapping[engine]


def _strip_prefix(prefix, d):
    l = len(prefix)
    gen = ( (key[l:], val)
            for key, val in d.iteritems()
            if key.startswith(prefix) )
    return dict(gen)

def _query2string(q,p):
    return q % tuple(("'%s'" % x for x in p))

class _dict_translator(object):
    def params(self, params):
        l = len(params)
        gen = ( ("p%d" % i, params[i]) for i in xrange(0,l) )
        return dict(gen)

    def query(self, q, l):
        psubst = tuple( ("%%(p%d)s" % i for i in xrange(0,l)) )
        w = q % psubst
        return w

class _qmark_translator(object):
    def params(self, params):
        return params
    def query(self, q, l):
        return q % tuple( ('?' for x in xrange(0,l)) )

_translator_map = {
        'pyformat'      : _dict_translator,
        'qmark'         : _qmark_translator
        }


class _Helper(object):
    engine = None       # database angine (a string) as defined in options
    options = {}        # database options
    module = None       # module corresponding to database engine
    modname = None      # name of database module
    trace = 0           # if if > 16 trace queries (quite slow)
    trans = None

    def __init__(self, opts, iface):
        self.ConfigError = iface.ConfigError
        self.DBError = iface.DBError

        if 'trace' in opts:
            self.trace = int(opts['trace'])

        try:
            self.engine = opts['engine']
        except KeyError:
            raise self.ConfigError("Database engine not specified",
                                opts['prefix'] + 'engine')
        try:
            self.modname = _engine2module(self.engine)
            __import__(self.modname)
            self.module = sys.modules[self.modname]
            self.trans = _translator_map[self.module.paramstyle]()
        except (KeyError, ImportError):
            raise self.ConfigError(
                    "Database engine not supported", self.engine)

        self.Error = self.module.Error


        for k in ['dsn', 'user', 'password', 'port', 'host', 'database']:
            if k in opts:
                self.options[k] = opts[k]

    def get_connection(self):
        return self.module.connect(**self.options)

    def execute(self, con, query, *params):
        cur = con.cursor()
        q = self.trans.query(query, len(params))
        p = self.trans.params(params)
        if self.trace > 16:
            logging.trace(__name__,
                    "Query on database %s:\n%s" %
                    (self.options['database'], _query2string(query, params)))
        cur.execute(q, p)
        return cur

    def execute_many(self, con, query, mparams):
        if self.trace > 16:
            mparams = list(mparams)
            logging.trace(__name__,
                    "Multiple query on database %s, first is:\n%s" %
                    (self.options['database'],
                    _query2string(query, mparams[0])))
        cur = con.cursor()
        l = query.count('%s')
        q = self.trans.query(query, l)
        p = [self.trans.params(p) for p in mparams]
        cur.executemany(q, p)
        return cur

    def execute_limited(self, con, limit, offset, query, *params):
        if not query.startswith('SELECT'):
            raise self.DBError("Internal sever error",
                    "Unsupported query time for limited execution: %s" %
                    query.split()[0])
        if limit >= 0:
            q = " LIMIT %d" % limit
            if offset >= 0:
                q += " OFFSET %d" % offset
            query += q
        return self.execute(con, query, *params)


def wrap(msg = None):
    def decor(method):
        def wrapper(self, *pargs, **kwargs):
            h = self._dbh
            try:
                return method(self,
                        h.get_connection(),
                        *pargs, **kwargs)
            except h.Error, e:
                if msg:
                    message = "Database failure while " + msg
                else:
                    message = "Database failure"
                if h.trace > 8:
                    logging.warning("FAILED: %s: %s: %s" %
                            (h.options['database'], message, e.message))
                raise h.DBError(message, e.message)
        return wrapper
    return decor

def make_helper(opts, prefix, iface):
    d = _strip_prefix(prefix, opts)
    d['prefix'] = prefix
    return _Helper(d, iface)

