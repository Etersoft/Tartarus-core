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
    return q % tuple(("'%s'" % x for x in params))

class _Helper(object):
    engine = None       # database angine (a string) as defined in options
    options = {}        # database options
    module = None       # module corresponding to database engine
    modname = None      # name of database module
    trace = None        # if if > 16 trace queries (quite slow)

    def __add_option(self, d, key):
        if self.prefix + key in d:
            self.options[key] = d[key]

    def __init__(self, opts, iface):
        self.ConfigError = iface.ConfigError
        self.DBError = iface.DBError

        if 'trace' in opts:
            self.trace = opts['trace']

        try:
            self.engine = opts['engine']
        except KeyError:
            raise self.ConfigError("Database engine not specified",
                                prefix + 'engine')
        try:
            self.modname = _engine2module(self.engine)
            __import__(self.modname)
            self.module = sys.modules[self.modname]
        except (KeyError, ImportError):
            raise self.ConfigError(
                    "Database engine not supported", self.engine)

        self.Error = self.module.Error

        for k in ['dsn', 'user', 'password', 'port', 'host', 'database']:
            if k in opts:
                self.options[k] = opts[k]

        # test wheter given connection parameters do work
        try:
            self.get_connection()
        except self.Error, e:
            raise self.DBError("Could not connect to database", e.message)


    def get_connection(self):
        return self.module.connect(**self.options)


    def __make_dict(self, params):
        l = len(params)
        gen = ( ("p%d" % i, params[i]) for i in xrange(0,l) )
        return dict(gen)

    def __translate_query(self, q, l):
        psubst = tuple( ("%%(p%d)s" % i for i in xrange(0,l)) )
        w = q % psubst
        return w

    def execute(self, con, query, *params):
        cur = con.cursor()
        q = self.__translate_query(query, len(params))
        p = self.__make_dict(params)
        if self.trace > 16:
            logging.trace(__name__, "Query on database %s:\n%s",
                    self.opts['database'],
                    _query2string(query, params))
        cur.execute(q, p)
        return cur

    def execute_many(self, con, query, mparams):
        cur = con.cursor()
        l = query.count('%s')
        q = self.__translate_query(query, l)
        p = [self.__make_dict(p) for p in mparams]
        if self.trace > 16:
            logging.trace(__name__,
                    "Multiple query on database %s, first is:\n%s",
                    self.opts['database'], _query2string(query, params))
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


def wrap(msg):
    def decor(method):
        def wrapper(self, *pargs, **kwargs):
            try:
                h = self._dbh
                return method(self,
                        h.get_connection(),
                        *pargs, **kwargs)
            except h.Error, e:
                if msg:
                    raise h.DBError(
                            "Database falure while " + msg, e.message)
                else:
                    raise h.DBError("Database falure", e.message)
        return wrapper
    return decor

def make_helper(opts, prefix, iface):
    return _Helper(_strip_prefix(prefix, opts), iface)

