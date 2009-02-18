from hostname import getdomain
from dns.resolver import query, NXDOMAIN
from Tartarus.system import Error

def check_krb5_lookup(domain = None):
    if not domain:
        domain = getdomain()

    try:
        realm_query = '_kerberos.' + domain
        realm = iter(query(realm_query,'TXT')).next().strings[0]
    except NXDOMAIN:
        raise Error('kerberos realm for domain "%s" not found'
                    % domain)

    try:
        kdc_query = '_kerberos._udp.' + realm + '.'
        iter(query(kdc_query,'SRV')).next()
    except NXDOMAIN:
        raise Error('kdc for REALM "%s" not found' % realm)

