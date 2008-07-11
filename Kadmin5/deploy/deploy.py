#!/usr/bin/env python

from __future__ import with_statement
import os

_acl_template = "*/admin@%(realm)s  *\n"

_kdc_conf_template = """
[kdcdefaults]
 acl_file = %(path)s/kadm5.acl
 dict_file = /usr/share/dict/words
 admin_keytab = %(path)s/kadm5.keytab

[realms]
 %(realm)s = {
  master_key_type = des-cbc-crc
 }
"""

_krb5_conf_template = """
[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log
 admin_server = FILE:/var/log/kadmind.log

[libdefaults]
 ticket_lifetime = 24000
 default_realm = %(realm)s
 dns_lookup_realm = false
 dns_lookup_kdc = false

[realms]
 %(realm)s = {
  kdc = %(fqdn)s:%(kdc_port)s
  admin_server = %(fqdn)s:%(admin_port)s
  default_domain = %(domain)s
 }

[domain_realm]
 %(domain)s = %(realm)s
 .%(domain)s = %(realm)s

[kdc]
 profile = %(path)s/kdc.conf
"""

def config(options):
    opts = {}
    opts['domain'] = options['DomainName']
    opts['realm'] = options['DomainName'].upper()
    opts['fqdn'] = options.get('KRB5.Server', 'kerberos' + options['DomainName'])
    opts['kdc_port'] = options.get('KRB5.KDCPort', 88)
    opts['admin_port'] = options.get('KRB5.KadminPort', 749)
    opts['path'] = '/var/lib/kerberos/krb5kdc'

    files = [
            ('./krb5.conf', _krb5_conf_template),
            (opts['path'] + '/kdc.conf', _kdc_conf_template),
            (opts['path'] + '/kadm5.acl', _acl_template)
            ]

    for file, template in files:
        with open(file,'w') as f:
            f.write(template % opts)

