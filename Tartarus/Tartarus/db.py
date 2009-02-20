"""Tartarus helpers for database.

Many modules of Tartarus work with relational databases. They usualy don't need
ORM, but need a clean, easy and portable way to execute simple SQL queries.

This module is a result of attempt to extract and improve common database code
from such modules.
"""

import sys
from functools import wraps
from Tartarus import logging
from Tartarus.iface import core as ICore

def _engine2module(engine):
    _engines_mapping = {
            'sqlite'        : 'sqlite',
            'sqlite2'       : 'sqlite',
            'sqlite3'       : 'sqlite3',
            'postgresql'    : 'psycopg2',
            'postgres'      : 'psycopg2'
            }
    return _engines_mapping[engine]


def _strip_prefix(prefix, dic):
    l = len(prefix)
    gen = ( (key[l:], val)
            for key, val in dic.iteritems()
            if key.startswith(prefix) )
    return dict(gen)

def _query2string(query, params):
    return query % tuple(("'%s'" % x for x in params))

class _Translator(object):
    def params(self, params):
        raise NotImplemented('Method not implemented: %s.%s.%s'
                % self.__module__, self.__class__, 'params')

    def query(self, template, params):
        raise NotImplemented('Method not implemented: %s.%s.%s'
                % self.__module__, self.__class__, 'query')

class _DictTranslator(_Translator):
    def params(self, params):
        l = len(params)
        gen = ( ("p%d" % i, params[i]) for i in xrange(0, l) )
        return dict(gen)

    def query(self, template, param_num):
        psubst = tuple( ("%%(p%d)s" % i
                         for i in xrange(0, param_num)) )
        w = template % psubst
        return w


class _QmarkTranslator(_Translator):
    def params(self, params):
        return params

    def query(self, template, param_num):
        return template % tuple( ('?' for x in xrange(0, param_num)) )


_translator_map = {
        'pyformat'      : _DictTranslator,
        'qmark'         : _QmarkTranslator
        }


def _enshure_dir(path):
    if not path:
        return
    import os
    p, f = os.path.split(path)
    if f.endswith('.db'):
        os.makedirs(p, mode=700)


class _Helper(object):
    def __init__(self, opts):
        self.ConfigError = ICore.ConfigError
        self.DBError = ICore.DBError

        self.trace = opts.get('trace', 0)
        try:
            self.trace = int(self.trace)
        except ValueError:
            raise self.ConfigError( "Invalid value for db.trace parametr "
                                    "(must be integer)", self.trace)
        try:
            self.engine = opts['engine']
        except KeyError:
            raise self.ConfigError("Database engine not specified",
                                opts['prefix'] + 'engine')
        try:
            self.modname = _engine2module(self.engine)
            __import__(self.modname)
            if 'sqlite' in self.modname:
                dbpath = opts.get('database')
                try:
                    _enshure_dir(dbpath)
                except OSError:
                    raise self.ConfigError('Bad database name', dbpath)

            self.module = sys.modules[self.modname]
            self.trans = _translator_map[self.module.paramstyle]()
        except (KeyError, ImportError):
            raise self.ConfigError(
                    "Database engine not supported", self.engine)

        self.Error = self.module.Error

        self.options = {}
        for k in ['dsn', 'user', 'password', 'port', 'host', 'database']:
            if k in opts:
                self.options[k] = opts[k]



    def get_connection(self):
        return self.module.connect(**self.options)

    def remove(self):
        """Destroy database permanently"""
        if self.engine.startswith('sqlite'):
            import os
            os.remove(self.options['database'])
        else:
            raise ICore.RuntimeError(
                   'Database removal unimplemented for %s', self.engine)


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
            if len(mparams) == 0:
                logging.trace(__name__,
                        "Multiple query with empty paramter list, %s" %
                        query)
            else:
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
        @wraps(method)
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

def make_helper(opts, prefix):
    d = _strip_prefix(prefix, opts)
    d['prefix'] = prefix
    return _Helper(d)

