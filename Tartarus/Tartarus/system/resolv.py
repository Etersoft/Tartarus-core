"""Resolver configuration manipulations.
"""

from __future__ import with_statement
import Tartarus.system.config as c

_RESOLV_CONF = "/etc/resolv.conf"

def get_nameservers(filename=_RESOLV_CONF):
    return c.config_get_file(filename, 'nameserver', delim='\s+')

def set_nameservers(nameservers, filename=_RESOLV_CONF):
    if not isinstance(nameservers, basestring):
        if len(nameservers) < 1 or len(nameservers) > 2:
            raise ValueError("Wrong number of nameservers: should be 1 or 2")
    return c.config_set_file(filename, 'nameserver', nameservers,
                             r_delim='\s+', w_delim=' ')

