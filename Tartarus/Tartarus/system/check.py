import hostname
import os, sys, string, time
import Ice, IcePy

from dns.resolver import query, NXDOMAIN

from Tartarus.system import Error
from Tartarus.client import getTimePrx, getDNSPrx



class ObjectNotExists(Exception):
    def __init__(self, msg):
        super(ObjectNotExists, self).__init__(msg)

def getServerTime(comm):
    t = getTimePrx(comm)
    return t.getTime()

def _getLocalTime():
    return int(time.time())

def _compare_Time(comm):
    if not comm:
        raise Error(' Can\'t get Ice communicator.\n Aborted.')
    try:
        serverTm = getServerTime(comm)
        if serverTm == None:
            Error(' Time service is not responding')
        localTm = _getLocalTime()
        if abs(serverTm-localTm) > 180:
            raise Error(' UTC time on server is not equal to utc local time.\n Please set time.\n Aborted.')
        return "Difference in time: %i" % (abs(serverTm-localTm))
    except Ice.ObjectNotExistException:
        raise ObjectNotExists(' Object Time doesn\'t exist')

def check_Time(comm):
    success = []
    error = []
    try:
        time = _compare_Time(comm)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s sec' % time)
    return success, error

def _exist_DNS(comm):
    if not comm:
        raise Error(' Can\'t get Ice communicator.\n Aborted.')
    try:
        ob = getDNSPrx (comm)
        if ob == None:
            raise Error('DNS: DNS is not responding')
        return "DNS: DNS exists and is responding"
    except Ice.ObjectNotExistException:
        raise ObjectNotExists('DNS: Object doesn\'t exist')

def check_DNS(comm):
    success = []
    error = []
    try:
        dns = _exist_DNS(comm)
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
        return realm, 'Kerberos realm for domain "%s" is "%s"' % (str(domain),str(realm))
    except NXDOMAIN:
        raise Error(' Kerberos realm for domain "%s" not found'
                    % domain)

def _check_krb5_kdc(realm):
    try:
        kdc_query = '_kerberos._udp.' + realm + '.'
        result = iter(query(kdc_query,'SRV')).next()
        return result, 'Kdc for REALM "%s" is "%s".' % (str(realm), str(result))
    except NXDOMAIN:
        raise Error('Kdc for REALM "%s" not found' % realm)

def _check_krb5_passwd(realm):
    try:
        kdc_query = '_kpasswd._udp.' + realm + '.'
        result = iter(query(kdc_query,'SRV')).next()
        return 'Kpasswd for REALM "%s" is "%s".' % (str(realm), str(result))
    except NXDOMAIN:
        raise Error('Kpasswd for REALM "%s" not found' % realm)

def _check_dns_CNAME(realm):
    try:
        kdc_query = 'kerberos.' + realm + '.'
        result = iter(query(kdc_query,'CNAME')).next()
        return 'CNAME record for kerberos is "%s".' % str(result)
    except NXDOMAIN:
        raise Error('CNAME record for kerberos not found')

def _check_record_A(record):
    try:
        kdc_query = str(record) + '.'
        result = iter(query(kdc_query,'A')).next()
        return result, 'A record for REALM "%s" is "%s".' % (str(record), str(result))
    except NXDOMAIN:
        raise Error(' A record for REALM was not found')


def _check_record_PTR(record):
    ip, _ = _check_record_A(record)
    try:
        rev_ip = str(ip).split('.')
        rev_ip.reverse()
        rev_ip = string.join(rev_ip, '.')
        rev_ip = rev_ip + '.in-addr.arpa.'
        kdc_query = rev_ip
        result = iter(query(kdc_query,'PTR')).next()
        if (record != str(result)):
            ip_record, _ = _check_record_A(str(record))
            if (ip != ip_record):
                raise Error ('ip "%s"  was got for this record "%s". But PTR record for this ip is "%s".' % (str(ip), record, str(result))) 
        return 'PTR record for ip "%s" is "%s".' % ( str(ip), str(result))
    except NXDOMAIN:
        raise Error(' PTR record for ip %s was not found' % str(ip))

def check_krb5_lookup(domain = None):
    success = []
    error = []
    realm = domain.upper()
    realmstr = 'Default kerberos realm for domain "%s" is %s' % (str(domain),str(realm))

    try:
        realm, realmstr = _check_krb5_realm(domain)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % realmstr)

    try:
        _, arecord = _check_record_A(domain)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % arecord)

    try:
        ptrrec = _check_record_PTR(domain)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % ptrrec)

    kdc = "kerberos." + domain
    kdcstr = 'Default Kdc for REALM "%s" is "%s".' % (str(realm), kdc)
    try:
        kdc, kdcstr = _check_krb5_kdc(realm)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % kdcstr)

    try:
        _, arecord = _check_record_A(str(kdc).split().pop().strip("."))
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % arecord)

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
    return realm, kdc, success, error

def _check_host(host = None):
    if not host:
        try:
            host = hostname.getname()
        except:
            raise Error('Hostname: Can\'t get hostname.\n Please check your network instalation.\n Aborted.')
    return "Hostname: %s" % host

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

def check_host_domain(host = None, domain = None, fqdn = None):
    success = []
    error = []
    try:
        hostname = _check_host(host)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % hostname)

    try:
        domainname = _check_domain(domain)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % domainname)

    try:
        fullhostname = _check_fqdn(fqdn)
    except Error, e:
        error.append('%s' % e)
    else:
        success.append('%s' % fullhostname)

    return success, error