"""Hosts local configuration manipulations.
"""

import Tartarus.system.config as c
import re

_HOSTS_CONF = "/etc/hosts"
_LOCAL_IP = "127.0.0.1"

def get_hosts(ip, filename=_HOSTS_CONF):
    return c.config_get_file(filename, ip, delim='\s+')

def get_localhosts(filename=_HOSTS_CONF):
    return get_hosts(_LOCAL_IP, filename)

def set_hosts(ip, hostnames, filename=_HOSTS_CONF):
    return c.config_set_file(filename, ip, hostnames,
                             r_delim='\s+', w_delim='\t')

def set_localhosts(hostnames, filename=_HOSTS_CONF):
    return set_hosts(_LOCAL_IP, hostnames, filename)

def _host_replace_filter(lines, hostname):
    expr = re.compile('^127\.0{1,3}\.0{1,3}\.0{,2}1*\s+(.*%s.*)'
                      % re.escape(hostname))
    for l in lines:
        m = expr.match(l)
        if m:
            yield '127.0.0.2\t%s\n' % m.group(1)
        else:
            yield l

replace_localhost_file = c._filter2file(_host_replace_filter)

def replace_localhost(hostname):
    replace_localhost_file(_HOSTS_CONF, hostname)
