

import Ice, IcePy

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

def soar2str(soar):
    return ('%(nameserver)s %(hostmaster)s %(serial)d %(refresh)d '
           '%(retry)d %(expire)d %(ttl)d' % soar.__dict__)

def str2soar(arg):
    (pr, hm, s, ref, ret, exp, ttl) = arg.split()
    return (pr, hm, long(s), long(ref), long(ret), long(exp), long(ttl))

