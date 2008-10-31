

import Ice, IcePy

class NoSuchObject(Ice.ObjectNotExistException):
    pass

import Tartarus
from Tartarus.iface import core as ICore

def proxy(cls, adapter, category, obj_name):
    if isinstance(adapter, IcePy.Current):
        adapter = adapter.adapter
    iden = Ice.Identity(obj_name, category)
    pr = adapter.createProxy(iden)
    return cls.uncheckedCast(pr)

def name(current, identity=None):
    """Get object name from current.

    Maybe later we'll want to apply some string convertions to it.
    """
    if identity:
        return identity.name
    return current.id.name

def soar2str(soar):
    return ('%(nameserver)s %(hostmaster)s %(serial)d %(refresh)d '
           '%(retry)d %(expire)d %(ttl)d' % soar.__dict__)

def str2soar(arg):
    (pr, hm, s, ref, ret, exp, ttl) = arg.split()
    return (pr, hm, long(s), long(ref), long(ret), long(exp), long(ttl))

def rev_zone_entry(addr):
    v = addr.split('.')
    if len(v) != 4:
        raise ICore.ValueError('Wrong IP address', addr)
    v.reverse()
    return '.'.join(v) + '.in-addr.arpa'
