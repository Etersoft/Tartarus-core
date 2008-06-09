

import Ice, IcePy
import db

from Ice import ObjectNotExistException as NoSuchObject

import Tartarus
from Tartarus.iface import DNS as I

def proxy(cls, ad, cat, name):
    if isinstance(ad, IcePy.Current):
        ad = ad.adapter
    id = Ice.Identity(name, cat)
    pr = ad.createProxy(id)
    return cls.uncheckedCast(pr)

def name(current, id=None):
    """Get object name from current.

    Maybe later we'll want to apply some string convertions to it.
    """
    if id:
        return id.name
    return current.id.name

def _make_dict(params):
    l = len(params)
    gen = ( ("p%d" % i, params[i]) for i in xrange(0,l) )
    return dict(gen)

def _translate_query(q, l):
    psubst = tuple( ("%%(p%d)s" % i for i in xrange(0,l)) )
    w = q % psubst
    return w


def execute(con, query, *params):
    cur = con.cursor()
    q = _translate_query(query, len(params))
    p = _make_dict(params)
    #print q % p
    cur.execute(q, _make_dict(params))
    return cur

def executemany(con, query, mparams):
    cur = con.cursor()
    l = query.count('%s')
    q = _translate_query(query, l)
    p = [_make_dict(p) for p in mparams]
    #print q % p[0]
    cur.executemany(q, p)
    return cur

def execute_limited(con, limit, offset, query, *params):
    if not query.startswith('SELECT'):
        raise ValueError("Internal sever error", "%d,%d" %(limit,offset))
    if limit >= 0:
        q = " LIMIT %d" % limit
        if offset >= 0:
            q += " OFFSET %d" % offset
        query += q
    return execute(con, query, *params)

def soar2str(soar):
    return ('%(nameserver)s %(hostmaster)s %(serial)d %(refresh)d '
           '%(retry)d %(expire)d %(ttl)d' % soar.__dict__)

def str2soar(arg):
    (pr, hm, s, ref, ret, exp, ttl) = arg.split()
    return (pr, hm, long(s), long(ref), long(ret), long(exp), long(ttl))

