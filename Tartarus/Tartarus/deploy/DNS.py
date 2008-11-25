
import Tartarus
from common import _checked_configure
from Tartarus.iface import DNS
from Tartarus.iface import core as C

SOA = DNS.SOARecord
R = DNS.Record
T = DNS.RecordType


_LOCAL_DATA = [
        ('localhost',
            SOA('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                R('localhost', T.NS, 'localhost', -1, -1),
                R('localhost', T.A,  '127.0.0.1', -1, -1)
            ]),
        ('127.in-addr.arpa',
            SOA('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                R('127.in-addr.arpa',       T.NS,  'localhost',   -1, -1),
                R('1.0.0.127.in-addr.arpa', T.PTR, 'localhost',   -1, -1),
                R('0.0.0.127.in-addr.arpa', T.PTR, 'localdomain', -1, -1)
            ]),
        ('localdomain',
            SOA('localhost', 'root.localhost',  0, 43200, 3600, 604800, 3600),
            [
                R('localdomain',           T.NS,    'localhost'),
                R('localdomain',           T.A,     '127.0.0.0'),
                R('localhost.localdomain', T.CNAME, 'localhost'),
            ]),
        ('0.in-addr.arpa',
            SOA('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                R('127.in-addr.arpa', T.NS, 'localhost', -1, -1)
            ]),
        ('255.in-addr.arpa',
            SOA('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                R('127.in-addr.arpa', T.NS, 'localhost', -1, -1)
            ])
    ]

def _process_zones(server, zonedata):
    for name, soar, records in zonedata:
        server.createZone(name, soar)
        zone = server.getZone(name)
        zone.addRecords(records)

def _mask2octets(mask):
    """Get a number of significant octetns in network address.

    The only argument is a network mask (an integer).
    """
    if isinstance(mask, basestring):
        mask = int(mask)
    if mask < 8 or mask >= 32:
        raise DNS.ConfigError("Wrong network mask", str(mask))
    if mask == 8:
        return 1
    if 8 < mask <= 16:
        return 2
    else:
        return 3

def _reverse_zone_name(addr, mask):
    """Using network address and mask, try to guess reverse zone name.
    """
    o = _mask2octets(int(mask))
    a = addr.split('.')
    a = a[:o]
    a.reverse()
    return '.'.join(a) + '.in-addr.arpa'



def _ptr_record(ip, fqdn, zone):
    """Make PTR record from ip, host fqdn and reverse zone name.

    zone is in form of [[b.]c.]d.in-addr.arpa (without a terminating dot)
    """
    octets = ip.split('.')
    octets.reverse()
    if len(octets) != 4:
        raise DNS.ConfigError('Invalud IPv4 adress', ip)

    n = zone.count('.')
    if n < 2:
        raise C.ConfigError('Invalid reverse zone name', zone)
    elif n > 4:
        name =  octets[0] + '.'
    else:
        name = '.'.join(octets[:(5-n)]) + '.'

    return DNS.Record(name + zone, DNS.RecordType.PTR, fqdn, -1, -1)


def deploy_dns(comm, opts):
    """Put inital data to DNS database and configure DNS server.

    @param comm
      a communicator. The following proxies should be available:
        - Tartarus.deployPrx.Server of type Tartarus::DNS::Server
        - Tartarys.deployPrx.DNSService of type Tartarus::core::Service
    @param opts
      a dictionary {name, value}. The following options are used:
          *Name*     *Type* *Madatory* *Comment*
          domainname String M          n/a
          ip         String M          n/a
          hostname   String M          n/a
          mask       Int    M          n/a
    """
    prx = comm.propertyToProxy('Tartarus.deployPrx.DNSService')
    _checked_configure(prx, opts.get('dns_force'))

    prx = comm.propertyToProxy('Tartarus.deployPrx.DNS')
    srv = DNS.ServerPrx.checkedCast(prx)

    _process_zones(srv, _LOCAL_DATA)

    domain = opts['domainname']
    ns = 'ns.' + domain
    krb = 'kerberos.' + domain
    ip = opts['ip']
    fqdn = opts['hostname']
    hostmaster = '%s.%s' % (opts['name'], domain)

    z = srv.createZone(domain,
            SOA(ns, hostmaster, 0, 43200, 3600, 604800, 3600))
    records = [
        R(domain,                     T.NS,    ns,             -1, -1),
        R(domain,                     T.A,     ip,             -1, -1),
        R(krb,                        T.CNAME, fqdn,           -1, -1),
        R('_kerberos._udp.' + domain, T.SRV,   '0 88 ' + krb,  0,  -1),
        R('_kerberos.' + domain,      T.TXT,   domain.upper(), -1, -1),
        ]
    if fqdn != domain:
        records.append( R(fqdn, T.A,     ip,   -1, -1))
    if ns != domain and ns != fqdn:
        records.append( R(ns,   T.CNAME, fqdn, -1, -1))
    z.addRecords(records)

    rzone = _reverse_zone_name(ip, opts['mask'])
    z = srv.createZone(rzone,
                       SOA(ns, hostmaster, 0, 43200, 3600, 604800, 3600))
    z.addRecords([ R(rzone, T.NS, ns, -1, -1),
                   _ptr_record(ip, fqdn, rzone) ])

    srv_opts = []
    if 'recursor' in opts:
        srv_opts.append(DNS.ServerOption('recursor', opts['recursor']))
    if 'allow_recursion' in opts:
        srv_opts.append(DNS.ServerOption('allow-recursion',
                                         opts['allow_recursion']))
    srv.setOptions(srv_opts)

