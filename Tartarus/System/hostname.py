from dns.resolver import query,NXDOMAIN
from dns.exception import DNSException
import socket

def gethostname():
    return socket.getfqdn()

def getdomain(fqdn = None):
    if not fqdn:
        try:
            fqdn = gethostname()
        except AttributeError:
            hostname = socket.gethostname()
            byaddr = socket.gethostbyaddr(socket.gethostbyname(hostname))
            aliases = byaddr[1]
            aliases.insert(0, byaddr[0])
            aliases.insert(0, hostname)
            for fqdn in aliases:
                if '.' in fqdn:
                    break
            else:
                raise 'domain not found for hostanme: "%s"' % hostname
    parts = fqdn.split('.')[1:]
    if parts == 0:
        raise 'domain not found for fqdn: "%s"' % fqdn
    return '.'.join(parts)

def sethostname():
    pass
