from Tartarus.system import Error
import socket

def getname():
    return socket.gethostname().split('.')[0]

def getfqdn():
    return socket.getfqdn()

def getdomain(fqdn = None):
    if not fqdn:
        try:
            fqdn = getfqdn()
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
                raise Error('domain not found for hostanme: "%s"' % hostname)
    parts = fqdn.split('.')[1:]
    if parts == 0:
        raise Error('domain not found for fqdn: "%s"' % fqdn)
    return '.'.join(parts)

def gethostname():
    return socket.gethostname()

def sethostname(hostname):
    raise Error('set hostname failed for "%s" (method not implemented yet)'
            % hostname)


def getsystemnets():
    try:
        import dnet
    except ImportError:
        addrs = socket.gethostbyname_ex(gethostname())[2]
    else:
        res = []
        def callback(addr, mas):
            mas.append(addr)
        dnet.intf().loop(callback, res)
        addrs = ( x.get('addr') for x in res )
        addrs = ( repr(x) for x in addrs if x )
    for a in addrs:
        if a.startswith('127.'):
            continue
        x = a.split('/')
        if len(x) == 2:
            yield x[0], x[1]
        else:
            yield x[0], None



