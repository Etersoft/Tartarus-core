
from __future__ import with_statement
import kadmin5, os

import Tartarus
from Tartarus.system.config import gen_config_from_file
from Tartarus.iface import SysDB, DNS, Kerberos
from Tartarus.iface import core as C

__all__ = ['deploy_sysdb', 'deploy_kadmin', 'deploy_dns']

# {{{1 Common code

def _checked_configure(svc_proxy, force, params = None):
    if not params:
        params = {}
    if not svc_proxy:
        raise C.RuntimeError('Proxy not found')

    svc = C.ServicePrx.checkedCast(svc_proxy)
    if not svc:
        raise C.RuntimeError('Wrong service proxy')

    if svc.isConfigured() and not force:
        raise C.RuntimeError('Database already exists')
    params['force'] = force
    svc.configure(params)


# {{{1 SysDB

def deploy_sysdb(comm, opts):
    """Put inital data to SysDB.

    @param comm
      a communicator. The following proxies should be available:
        - Tartarus.deployPrx.UserManager of type Tartarus::SysDB::UserManager
        - Tartarus.deployPrx.GroupManager of type Tartarus::SysDB::GroupManager
        - Tartarys.deployPrx.SysDBService of type Tartarus::core::Service
    @param opts
      a dictionary { option name : option value }. The following options are used
          *Name* *Type* *Madatory* *Comment*
          name   String M          n/a
    """
    prx = comm.propertyToProxy('Tartarus.deployPrx.SysDBService')
    _checked_configure(prx, opts.get('sysdb_force'))

    prx = comm.propertyToProxy('Tartarus.deployPrx.UserManager')
    um = SysDB.UserManagerPrx.checkedCast(prx)
    prx = comm.propertyToProxy('Tartarus.deployPrx.GroupManager')
    gm = SysDB.GroupManagerPrx.checkedCast(prx)

    admins_gid = gm.create(SysDB.GroupRecord(-1, "admins",
                                             "System administartors"))
    users_gid = gm.create(SysDB.GroupRecord(-1, "users", "Users"))

    uid = um.create(SysDB.UserRecord(-1, admins_gid, opts['name'],
                                     "System administrator"))
    gm.addUsers(users_gid, [uid])



# {{{1 Kadmin5

def _get_stash_password(opts):
    """Return a string to be used as password for Kerberos database.

    If a password is supplyed by user, return it. If not, try to read it from
    /dev/urandom or return hardcoded default.
    """
    if 'stash_password' in opts:
        return opts['stash_password']
    try:
        with open('/dev/urandom') as f:
            s = f.read(128)
            return s.replace('\0','Q')
    except Exception:
        return ';lxdfz,cmxfz45'


def deploy_kadmin(comm, opts):
    """Put inital data to Kerberos database.

    @param comm
      a communicator. The following proxies should be available:
        - Tartarus.deployPrx.Kadmin of type Tartarus::Kerberos::Kadmin
        - Tartarus.deployPrx.KerberosService of type Tartarus::core::Service
    @param opts
      a dictionary {option name: option value}. The following options are used:
          *Name*       *Type* *Madatory* *Comment*
          name         string M          n/a
          password     string M          n/a
          hostname     string M          n/a
          domainname   string M          n/a
          kdc_port     int    O          n/a
          kadmin_port  int    O          n/a
          kdc_cfg_path string O          n/a
    """
    k5opts = {
        'realm'       : opts['domainname'].upper(),
        'domain'      : opts['domainname'],
        'kdc_port'    : str(opts.get('kdc_port', 88)),
        'kadmin_port' : str(opts.get('kadmin_port', 749)),
        'password'    : _get_stash_password(opts) }

    prx = comm.propertyToProxy('Tartarus.deployPrx.KerberosService')
    _checked_configure(prx, opts.get('krb_force'), k5opts)

    prx = comm.propertyToProxy('Tartarus.deployPrx.Kadmin')
    ka = Kerberos.KadminPrx.checkedCast(prx)

    ka.createPrincipal(opts['name'], opts['password'])
    spr = ka.createServicePrincipal('host', opts['hostname'])

    keytab = kadmin5.keytab()

    # remove all other keys of this principal (from previous deployments?)
    try:
        keytab.remove_princ(spr.name)
    except RuntimeError, e:
        if e.args[0] != os.errno.ENOENT:
            raise

    for k in spr.keys:
        keytab.add_entry(spr.name, k.kvno, k.enctype, k.data)


# {{{1 DNS

SOA = DNS.SOARecord
R = DNS.Record
T = DNS.RecordType

# {{{2 records for localhost and such stuff

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

# {{{2 DNS helper functions

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

# 2}}}


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

#    subnet = make_subnet(ip, mask)
#    srv_opts = []
#    if 'DNS.Recursor' in opts:
#        srv_opts.append(DNS.ServerOption('recursor', opts['DNS.Recursor']))
#        srv_opts.append(DNS.ServerOption('allow-recursion', subnet))
#    srv.setOptions(srv_opts)

