from __future__ import with_statement
import sys

import Tartarus, os
from common import _checked_configure
from Tartarus.iface import Kerberos
from Tartarus.deploy import save_keys
from Tartarus.deploy.common import feature, after, before
from Tartarus.system import service
from Tartarus import system

@feature('kerberos')
@after('service_init', 'sysdb_checks')
@before('service_checks_done')
def kerberos_checks(wiz):
    wiz.dialog.info('Checking for Kadmin5...')
    if 'sysdb' not in wiz.features:
        return 'KDC can\'t be configured without SysDB.'
    prx = wiz.comm.propertyToProxy("Tartarus.deployPrx.KerberosService")
    try:
        s = Tartarus.iface.core.ServicePrx.checkedCast(prx)
    except:
        return 'SysDB service not found. It may be not to be installed.'
    if not s:
        return 'SysDB service not found. It may be not to be installed.'
    if s.isConfigured():
        prompt = "Kerberos configuration already exists. Force reinitialization?"
        if not wiz.dialog.force(prompt):
            return 'Deployment canceled'
    wiz.krb_service = s

@feature('kerberos')
@after('kerberos_checks', 'sysdb_dialog', 'service_checks_done')
@before('service_dialog_done')
def kerberos_dialog(wiz):
    if 'users' not in wiz.opts:
        return 'Options do not contains users. This should not be happen!'
    _set_domain(wiz)
    _set_hostname(wiz)

def _set_domain(wiz):
    if 'domain' in wiz.opts: return
    domain = system.hostname.getdomain()
    domain = wiz.dialog.ask("Enter domain name for KDC server", domain)
    q.opts['domain'] = domain

def _set_hostname(wiz):
    if 'hostname' in wiz.opts: return
    wiz.opts['hostname'] = ".".join([system.hostname.getname(), wiz.opts['domain']])

@feature('kerberos')
@after('kerberos_dialog', 'service_dialog_done')
@before('service_restart')
def kerberos_deploy(wiz):
    wiz.dialog.info('Configuring KDC...')
    opts = wiz.opts
    k5opts = {
        'realm'       : opts['domain'].upper(),
        'domain'      : opts['domain'],
        'kdc_port'    : str(opts.get('kdc_port', 88)),
        'kadmin_port' : str(opts.get('kadmin_port', 749)),
        'password'    : _get_stash_password(opts),
        'force'       : 'force' }

    wiz.krb_service.configure(k5opts)

    prx = wiz.comm.propertyToProxy('Tartarus.deployPrx.Kadmin')
    ka = Kerberos.KadminPrx.checkedCast(prx)

    for name, _, password, _ in wiz.opts['users']:
        ka.createPrincipal(name, password)
    save_keys(ka.createServicePrincipal('host', opts['hostname']))
    save_keys(ka.createServicePrincipal('host', opts['domain']))

@feature('kerberos')
@after('kerberos_deploy')
@before('service_restart')
def krb_restart_services(wiz):
    for s in ['krb5kdc', 'kadmin']:
        service.service_on(s)
        service.service_restart(s)

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
          domain       string M          n/a
          kdc_port     int    O          n/a
          kadmin_port  int    O          n/a
          kdc_cfg_path string O          n/a
    """
    k5opts = {
        'realm'       : opts['domain'].upper(),
        'domain'      : opts['domain'],
        'kdc_port'    : str(opts.get('kdc_port', 88)),
        'kadmin_port' : str(opts.get('kadmin_port', 749)),
        'password'    : _get_stash_password(opts) }

    prx = comm.propertyToProxy('Tartarus.deployPrx.KerberosService')
    _checked_configure(prx, opts.get('krb_force'), k5opts)

    prx = comm.propertyToProxy('Tartarus.deployPrx.Kadmin')
    ka = Kerberos.KadminPrx.checkedCast(prx)

    ka.createPrincipal(opts['name'], opts['password'])
    save_keys(ka.createServicePrincipal('host', opts['hostname']))
    save_keys(ka.createServicePrincipal('host', opts['domain']))

