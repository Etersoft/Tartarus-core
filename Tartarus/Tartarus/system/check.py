import Tartarus.system.hostname as hostname
from dns.resolver import query, NXDOMAIN
from Tartarus.system import Error

def check_krb5_realm(domain = None):
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

def check_krb5_kdc(realm):
    try:
        kdc_query = '_kerberos._udp.' + realm + '.'
        return iter(query(kdc_query,'SRV')).next()
    except NXDOMAIN:
        raise Error('kdc for REALM "%s" not found' % realm)

def check_krb5_passwd(realm):
    try:
        kdc_query = '_kpasswd._udp.' + realm + '.'
        return iter(query(kdc_query,'SRV')).next()
    except NXDOMAIN:
        raise Error('kpasswd for REALM "%s" not found' % realm)

def check_krb5_lookup():
    realm = check_krb5_realm()
    check_krb5_kdc(realm)
    check_krb5_passwd(realm)

def check_host(host = None):
    if not host:
        try:
            host = hostname.getname()
        except:
            raise Error('Can\'t get hostname.\n Please check your network instalation.\n Aborted.')

def check_domain(domain = None):
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

def check_fqdn(fqdn = None):
    if not fqdn:
        try:
            fqdn = hostname.getfqdn()
        except:
            raise Error('Can\'t get full hostname.\n Please check your network instalation.\n Aborted.')
    if fqdn.find('.') < 0:
        raise Error('Uncorrect full hostname \'%s\'.\n Please check your full hostname: it must have points.\n Aborted.' % fqdn)
    if len(fqdn) < 3:
        raise Error('Uncorrect full hostname \'%s\'.\n Please check your full hostname: it is too small.\n Aborted.' % fqdn)
