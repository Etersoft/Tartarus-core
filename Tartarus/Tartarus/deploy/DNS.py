import sys
import socket

import Tartarus
from Tartarus import system
from common import _checked_configure
from Tartarus.iface import DNS
from Tartarus.iface import core as C
from Tartarus.deploy.common import feature, after, before
import Tartarus.system.resolv as resolv
from Tartarus.system import service

SOA = DNS.SOARecord
R = DNS.Record
T = DNS.RecordType

@feature('dns')
@after('service_init')
@before('service_checks_done')
def dns_checks(wiz):
    wiz.dialog.info('Checking for DNS...')
    prx = wiz.comm.propertyToProxy("Tartarus.deployPrx.DNSService")
    try:
        s = Tartarus.iface.core.ServicePrx.checkedCast(prx)
    except:
        return 'DNS service not found. It may be not to be installed.'
    if not s:
        return 'DNS service not found. It may be not to be installed.'
    if s.isConfigured():
        prompt = "DNS configuration already exists. Force reinitialization?"
        if not wiz.dialog.force(prompt):
            return 'Deployment canceled'
    wiz.dns_service = s

@feature('dns')
@after('dns_checks', 'sysdb_dialog')
@before('service_dialog_done')
def dns_dialog(wiz):
    _set_domain(wiz)
    _set_hostmaster(wiz)
    _set_hostname(wiz)
    _set_addr2mask(wiz)
    _set_ip(wiz)
    _set_mask(wiz)
    configure_recursor(wiz)
    configure_resolv(wiz)

def _set_domain(wiz):
    if 'domain' in wiz.opts: return
    domain = system.hostname.getdomain()
    domain = wiz.dialog.ask("Enter domain name for DNS server", domain)
    q.opts['domain'] = domain

def _set_hostmaster(wiz):
    if 'hostmaster' in wiz.opts: return
    if 'users' in wiz.opts:
        hostmaster = wiz.opts['users'][0][0]
    domain = wiz.opts['domain']
    hostmaster = wiz.dialog.ask('Hostmaster for %s DNS domain?' % domain, hostmaster)
    wiz.opts['hostmaster'] = '%s.%s' % (hostmaster, domain)

def _set_hostname(wiz):
    if 'hostname' in wiz.opts: return
    wiz.opts['hostname'] = ".".join([system.hostname.getname(), wiz.opts['domain']])

def _set_addr2mask(wiz):
    try:
        wiz.dns_addr2mask = dict(system.hostname.getsystemnets())
    except socket.error, e:
        wiz.fail("Faild to get address information for this host.\n"
                 "The error was: %s\n"
                 "Please check your network configuration."
                 % e.args[1])

def _set_ip(wiz):
    if 'ip' in wiz.opts: return
    ip = wiz.dialog.choice("The ip address of server will be", wiz.dns_addr2mask.keys())
    if not ip: wiz.fail("Deployment canceled!")
    wiz.opts['ip'] = ip

def _set_mask(wiz):
    if 'mask' in wiz.opts: return
    try:
        idx = SUPPORTED_MASKS.index(wiz.dns_addr2mask[wiz.opts['ip']])
    except ValueError:
        idx = SUPPORTED_MASKS.index('24')
    mask = wiz.dialog.choice("The network mask for server will be",
                              SUPPORTED_MASKS, idx)
    if not mask: wiz.fail("Deployment canceled!")
    wiz.opts['mask'] = mask

SUPPORTED_MASKS = ['8', '16', '24']

def _is_valid_ip(s):
    l = s.split('.')
    if len(l) != 4:
        return False
    for x in l:
        try:
            i = int(x)
            if i < 0 or i > 255:
                return False
        except ValueError:
            return False
    return True

def configure_recursor(wiz):
    if not wiz.dialog.yesno("Configure DNS server to use upper-level DNS?"):
        return
    ns = resolv.get_nameservers()
    ns = [x for x in ns
          if not x.startswith('127.') and not x.startswith('localhost')]
    while True:
        r = wiz.dialog.choice("Address of upper-level DNS server:", ns)
        if not isinstance(r, basestring):
            continue
        if not _is_valid_ip(r):
            wiz.dialog.error("This is not valid IPv4 address.")
            continue
        try:
            if socket.inet_aton(r) == socket.inet_aton(wiz.opts['ip']):
                wiz.dialog.error("This address should not coinside with your server")
                continue
        except socket.error:
            continue
        wiz.opts['recursor'] = r
        wiz.opts['allow_recursion'] = '127.0.0.1/8 %s/%s' % (
                wiz.opts['ip'], wiz.opts['mask'])
        break

def configure_resolv(wiz):
    if wiz.dialog.yesno("Use local DNS server on this host?"):
        wiz.opts['dns_use_self'] = 'true'
    if 'recursor' in wiz.opts:
        if wiz.dialog.yesno("Use %s on this host as a secondary nameserver?"
                     % wiz.opts['recursor']):
            wiz.opts['dns_use_recursor'] = 'true'


@feature('dns')
@after('service_dialog_done', 'dns_dialog')
@before('service_restart')
def dns_deploy(wiz):
    wiz.dialog.info('Configuring DNS...')

    opts = wiz.opts
    wiz.dns_service.configure({'force': 'force'})
    prx = wiz.comm.propertyToProxy('Tartarus.deployPrx.DNS')
    srv = DNS.ServerPrx.checkedCast(prx)

    _process_zones(srv, _LOCAL_DATA)

    domain = opts['domain']
    ns = 'ns.' + domain
    krb = 'kerberos.' + domain
    ip = opts['ip']
    fqdn = opts['hostname']
    hostmaster = opts['hostmaster']

    z = srv.createZone(domain,
            SOA(ns, hostmaster, 0, 43200, 3600, 604800, 3600))
    records = [
        R(domain,                     T.NS,    ns,             -1, -1),
        R(domain,                     T.A,     ip,             -1, -1),
        R(krb,                        T.CNAME, fqdn,           -1, -1),
        R('_kerberos._udp.' + domain, T.SRV,   '0 88 ' + krb,  0,  -1),
        R('_kerberos._tcp.' + domain, T.SRV,   '0 88 ' + krb,  0,  -1),
        R('_kpasswd._udp.' + domain,  T.SRV,   '0 464 ' + krb,  0,  -1),
        R('_kerberos-adm._tcp.' + domain, T.SRV, '0 749 ' + krb,  0,  -1),
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

@feature('dns')
@after('dns_deploy')
@before('service_restart')
def dns_restart(wiz):
    service.service_on('powerdns')
    service.service_restart('powerdns')

@feature('dns')
@after('dns_restart')
def dns_set_resolver(wiz):
    nameservers = []
    if 'dns_use_self' in wiz.opts:
        nameservers.append('127.0.0.1')
    if 'dns_use_recursor' in wiz.opts:
        nameservers.append(wiz.opts['recursor'])
    if len(nameservers):
        resolv.set_nameservers(nameservers)

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
          domain     String M          n/a
          ip         String M          n/a
          hostname   String M          n/a
          mask       Int    M          n/a
    """
    prx = comm.propertyToProxy('Tartarus.deployPrx.DNSService')
    _checked_configure(prx, opts.get('dns_force'))

    prx = comm.propertyToProxy('Tartarus.deployPrx.DNS')
    srv = DNS.ServerPrx.checkedCast(prx)

    _process_zones(srv, _LOCAL_DATA)

    domain = opts['domain']
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
        R('_kerberos._tcp.' + domain, T.SRV,   '0 88 ' + krb,  0,  -1),
        R('_kpasswd._udp.' + domain,  T.SRV,   '0 464 ' + krb,  0,  -1),
        R('_kerberos-adm._tcp.' + domain, T.SRV, '0 749 ' + krb,  0,  -1),
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

