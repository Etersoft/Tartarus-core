import hostname
import os, sys, string, time
import Ice, IcePy

from dns.resolver import query, NXDOMAIN
from Tartarus.iface import Time
from Tartarus.system import Error

class ObjectNotExists(Exception):
    def __init__(self, msg):
        super(ObjectNotExists, self).__init__(msg)

def _serverTimePrx(domain):
    pr = Ice.createProperties()
    idata = Ice.InitializationData()
    idata.properties = pr
    pr.load("/etc/Tartarus/deploy/client-deploy.conf")
    comm = Ice.initialize(idata)
    prx = comm.stringToProxy('Time/Server: ssl -h %s -p 12345' % domain)
    t = Time.ServerPrx.checkedCast(prx)
    return t.getTime()

def _getLocalTime():
    return int(time.time())

def _compare_Time(domain = None):
    if not domain:
        try:
            domain = hostname.getdomain()
        except:
            raise Error(' Can\'t get domain name.\n Please check your network instalation.\n Aborted.')
    try:
        serverTm = _serverTimePrx(domain)
        if serverTm == None:
            Error(' Time service is not responding')
        localTm = _getLocalTime()
        if abs(serverTm-localTm) > 180:
            raise Error(' UTC time on server is not equal to utc local time.\n Please set time.\n Aborted.')
        return "Difference in time: %i" % (abs(serverTm-localTm))
    except Ice.ObjectNotExistException:
        raise ObjectNotExists(' Object Time doesn\'t exist')

def check_Time(domain = None):
    success = []
    error = []
    try:
        time = _compare_Time()
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s sec' % time)
    return success, error

def _serverDNSPrx(domain):
    pr = Ice.createProperties()
    idata = Ice.InitializationData()
    idata.properties = pr
    pr.load("/etc/Tartarus/deploy/client-deploy.conf")
    comm = Ice.initialize(idata)
    prx = comm.stringToProxy(' DNS/Server: ssl -h %s -p 12345' % domain)
    return IcePy.ObjectPrx.checkedCast(prx)

def _exist_DNS(domain = None):
    if not domain:
        try:
            domain = hostname.getdomain()
        except:
            raise Error('DNS: Can\'t get domain name.\n Please check your network instalation.\n Aborted.')
    try:
        ob = _serverDNSPrx(domain)
        if ob == None:
            raise Error('DNS: DNS is not responding')
        return "DNS: DNS exists and is responding"
    except Ice.ObjectNotExistException:
        raise ObjectNotExists('DNS: Object doesn\'t exist')

def check_DNS(domain = None):
    success = []
    error = []
    try:
        dns = _exist_DNS()
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % dns)
    return success, error

def _check_krb5_realm(domain = None):
    if not domain:
        try:
            domain = hostname.getdomain()
        except:
            raise Error(' Can\'t get domain name.\n Please check your network instalation.\n Aborted.')
    realm_query = '_kerberos.' + domain
    try:
        realm = iter(query(realm_query,'TXT')).next().strings[0]
        return realm, 'Kerberos realm for domain "%s" is %s' % (str(domain),str(realm))
    except NXDOMAIN:
        raise Error(' Kerberos realm for domain "%s" not found'
                    % domain)

def _check_krb5_kdc(realm):
    try:
        kdc_query = '_kerberos._udp.' + realm + '.'
        result = iter(query(kdc_query,'SRV')).next()
        return 'Kdc for REALM "%s" is %s.' % (str(realm), str(result))
    except NXDOMAIN:
        raise Error('Kdc for REALM "%s" not found' % realm)

def _check_krb5_passwd(realm):
    try:
        kdc_query = '_kpasswd._udp.' + realm + '.'
        result = iter(query(kdc_query,'SRV')).next()
        return 'Kpasswd for REALM "%s" is %s.' % (str(realm), str(result))
    except NXDOMAIN:
        raise Error('Kpasswd for REALM "%s" not found' % realm)

def _check_dns_CNAME(realm):
    try:
        kdc_query = 'kerberos.' + realm + '.'
        result = iter(query(kdc_query,'CNAME')).next()
        return 'CNAME record for kerberos is %s.' % str(result)
    except NXDOMAIN:
        raise Error('CNAME record for kerberos not found')

def _check_dns_A(realm):
    try:
        kdc_query = realm + '.'
        result = iter(query(kdc_query,'A')).next()
        return result, 'A record for REALM "%s" is %s.' % (str(realm), str(result))
    except NXDOMAIN:
        raise Error(' A record for REALM was not found')


def _check_dns_PTR(realm):
    ip, _ = _check_dns_A(realm)
    try:
        rev_ip = str(ip).split('.')
        rev_ip.reverse()
        rev_ip = string.join(rev_ip, '.')
        rev_ip = rev_ip + '.in-addr.arpa.'
        kdc_query = rev_ip
        result = iter(query(kdc_query,'PTR')).next()
        return 'PTR record for ip "%s" is %s.' % ( str(ip), str(result))
    except NXDOMAIN:
        raise Error(' PTR record for ip %s was not found' % str(ip))

def check_krb5_lookup():
    success = []
    error = []
    try:
        realm, realmstr = _check_krb5_realm()
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % realmstr)

    try:
        kdc = _check_krb5_kdc(realm)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % kdc)

    try:
        kpasswd = _check_krb5_passwd(realm)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % kpasswd)

    try:
        cname = _check_dns_CNAME(realm)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % cname)

    try:
        _, arecord = _check_dns_A(realm)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % arecord)

    try:
        ptrrec = _check_dns_PTR(realm)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % ptrrec)
    return success, error

def _check_host(host = None):
    if not host:
        try:
            host = hostname.getname()
            return "Hostname: %s" % host
        except:
            raise Error('Hostname: Can\'t get hostname.\n Please check your network instalation.\n Aborted.')


def _check_domain(domain = None):
    if not domain:
        try:
            domain = hostname.getdomain()
        except:
            raise Error('Domain: Can\'t get domain name.\n Please check your network instalation.\n Aborted.')

    if domain.find('.') < 0:
        raise Error('Domain: Can\'t enter in to \'%s\' domain.\n Please check your domain name: it must have points.\n Aborted.' % domain)

    if len(domain) < 2:
        raise Error('Domain: Can\'t enter in to \'%s\' domain.\n Please check your domain name: it is too small.\n Aborted.' % domain)

    if domain.endswith('.localdomain') or domain.endswith('.localdomain.'):
        raise Error('Domain: Can\'t enter in to \'%s\' domain.\n Please check your domain name: it must not be \'localdomain\'.\n Aborted.' % domain)

    return "Domain: %s" % domain

def _check_fqdn(fqdn = None):
    if not fqdn:
        try:
            fqdn = hostname.getfqdn()
        except:
            raise Error('Full hostname: Can\'t get full hostname.\n Please check your network instalation.\n Aborted.')

    if fqdn.find('.') < 0:
        raise Error('Full hostname: Uncorrect full hostname \'%s\'.\n Please check your full hostname: it must have points.\n Aborted.' % fqdn)

    if len(fqdn) < 3:
        raise Error('Full hostname: Uncorrect full hostname \'%s\'.\n Please check your full hostname: it is too small.\n Aborted.' % fqdn)

    return "Full hostname: %s" % fqdn

def check_host_domain():
    success = []
    error = []
    try:
        hostname = _check_host()
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % hostname)

    try:
        domainname = _check_domain()
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % domainname)

    try:
        fullhostname = _check_fqdn()
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % fullhostname)

    return success, error