from __future__ import with_statement

import Tartarus, os
from common import _checked_configure
from Tartarus.iface import Kerberos
from Tartarus.deploy import save_keys

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
    save_keys(ka.createServicePrincipal('host', opts['hostname']))
    save_keys(ka.createServicePrincipal('host', opts['domainname']))

