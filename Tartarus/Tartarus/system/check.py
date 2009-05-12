#!/usr/bin/python
import Tartarus.system.hostname as hostname
from dns.resolver import query, NXDOMAIN
from Tartarus.system import Error
import os, string, time
import Ice, IcePy

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
    return t.getTime()

def _getLocalTime():
    return int(time.time())

def check_Time(domain = None):
    if not domain:
        try:
            domain = hostname.getdomain()
        except:
            raise Error('Can\'t get domain name.\n Please check your network instalation.\n Aborted.')
    try:
        serverTm = _serverTimePrx(domain)
        if ob == None:
            Error('Time service is not responding')
        localTm = _getLocalTime()
        if abs(serverTm-localTm) > 180:
            raise Error('UTC time on server is not equal to utc local time.\n Please set time.\n Aborted.')
    except Ice.ObjectNotExistException:
        raise ObjectNotExists('Object Time doesn\'t exist')

def _serverDNSPrx(domain):
    pr = Ice.createProperties()
    idata = Ice.InitializationData()
    idata.properties = pr
    pr.load("/etc/Tartarus/deploy/client-deploy.conf")
    comm = Ice.initialize(idata)
    prx = comm.stringToProxy('DNS/Server: ssl -h %s -p 12345' % domain)
    return IcePy.ObjectPrx.checkedCast(prx)

def check_DNS(domain = None):
    if not domain:
        try:
            domain = hostname.getdomain()
        except:
            raise Error('Can\'t get domain name.\n Please check your network instalation.\n Aborted.')
    try:
        ob = _serverDNSPrx(domain)
        if ob == None:
            Error('DNS is not responding')
    except Ice.ObjectNotExistException:
        raise ObjectNotExists('Object doesn\'t exist')

def _check_krb5_realm(domain = None):
    if not domain:
        try:
            domain = hostname.getdomain()
        except:
            raise Error('Can\'t get domain name.\n Please check your network instalation.\n Aborted.')
    realm_query = '_kerberos.' + domain
    try:
        realm = iter(query(realm_query,'TXT')).next().strings[0]
        return realm
    except NXDOMAIN:
        raise Error('kerberos realm for domain "%s" not found'
                    % domain)

def _check_krb5_kdc(realm):
    try:
        kdc_query = '_kerberos._udp.' + realm + '.'
        return iter(query(kdc_query,'SRV')).next()
    except NXDOMAIN:
        raise Error('kdc for REALM "%s" not found' % realm)

def _check_krb5_passwd(realm):
    try:
        kdc_query = '_kpasswd._udp.' + realm + '.'
        return iter(query(kdc_query,'SRV')).next()
    except NXDOMAIN:
        raise Error('kpasswd for REALM "%s" not found' % realm)

def _check_dns_CNAME(realm):
    try:
        kdc_query = 'kerberos.' + realm + '.'
        return iter(query(kdc_query,'CNAME')).next()
    except NXDOMAIN:
        raise Error('CNAME record for kerberos not found')

def _check_dns_A(realm):
    try:
        kdc_query = realm + '.'
        return iter(query(kdc_query,'A')).next()
    except NXDOMAIN:
        raise Error('A record for REALM was not found')

def _check_dns_PTR(realm):
    ip = _check_dns_A(realm)
    try:
        rev_ip = str(ip).split('.')
        rev_ip.reverse()
        rev_ip = string.join(rev_ip, '.')
        rev_ip = rev_ip + '.in-addr.arpa.'
        kdc_query = rev_ip
        return iter(query(kdc_query,'PTR')).next()
    except NXDOMAIN:
        raise Error('PTR record for REALM was not found')

def check_krb5_lookup():
    realm = _check_krb5_realm()
    _check_krb5_kdc(realm)
    _check_krb5_passwd(realm)
    _check_dns_CNAME(realm)
    _check_dns_A(realm)
    _check_dns_PTR(realm)

def _check_host(host = None):
    if not host:
        try:
            host = hostname.getname()
        except:
            raise Error('Can\'t get hostname.\n Please check your network instalation.\n Aborted.')

def _check_domain(domain = None):
    if not domain:
        try:
            domain = hostname.getdomain()
        except:
            raise Error('Can\'t get domain name.\n Please check your network instalation.\n Aborted.')

    if domain.find('.') < 0:
        raise Error('Can\'t enter in to \'%s\' domain.\n Please check your domain name: it must have points.\n Aborted.' % domain)
    if len(domain) < 2:
        raise Error('Can\'t enter in to \'%s\' domain.\n Please check your domain name: it is too small.\n Aborted.' % domain)
    if domain.endswith('.localdomain') or domain.endswith('.localdomain.'):
        raise Error('Can\'t enter in to \'%s\' domain.\n Please check your domain name: it must not be \'localdomain\'.\n Aborted.' % domain)

def _check_fqdn(fqdn = None):
    if not fqdn:
        try:
            fqdn = hostname.getfqdn()
        except:
            raise Error('Can\'t get full hostname.\n Please check your network instalation.\n Aborted.')
    if fqdn.find('.') < 0:
        raise Error('Uncorrect full hostname \'%s\'.\n Please check your full hostname: it must have points.\n Aborted.' % fqdn)
    if len(fqdn) < 3:
        raise Error('Uncorrect full hostname \'%s\'.\n Please check your full hostname: it is too small.\n Aborted.' % fqdn)

def check_host_domain():
    _check_host()
    _check_domain()
    _check_fqdn()

def main():
    try:
        print "Check host and domain: "
        check_host_domain()
    except Error, e:
        print '\033[91mFAIL\033[0m (%s)\n' % e
    else:
        print '\033[92mDONE\033[0m\n'

    try:
        print "Check time on server and localtime: "
        check_Time()
    except Error, e:
        print '\033[91mFAIL\033[0m (%s)\n' % e
    else:
        print '\033[92mDONE\033[0m\n'

    try:
        print "Check kerberos: "
        check_krb5_lookup()
    except Error, e:
        print '\033[91mFAIL\033[0m (%s)\n' % e
    else:
        print '\033[92mDONE\033[0m\n'

    try:
        print "Check DNS: "
        check_DNS()
    except Error, e:
        print '\033[91mFAIL\033[0m (%s)\n' % e
    else:
        print '\033[92mDONE\033[0m\n'

if __name__ == '__main__':
    main()