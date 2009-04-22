from __future__ import with_statement
import os
import krb5user
from Tartarus.system import config, service, pam
from Tartarus.deploy import save_keys
from Tartarus.system.krbconf import Krb5Conf
import Tartarus.system.hostname as hostname
from Tartarus.deploy.common import feature, after, before
from Tartarus.client import initialize
from Tartarus.iface import DHCP, Kerberos, core

_all_template = '/usr/share/Tartarus/templates/all/common.conf.template'

@feature('client')
def client_chkroot(wiz):
    if os.getuid() != 0:
        return 'Only root can do this'

@feature('client')
def client_conf(wiz):
    if 'hostname' not in wiz.opts:
        wiz.opts['hostname'] = wiz.dialog.ask('Hostname for this computer will be', hostname.getname())
    if 'domain' not in wiz.opts:
        wiz.opts['domain'] = wiz.dialog.ask('Tartarus domain to join', hostname.getdomain())
    if 'fqdn' not in wiz.opts:
        wiz.opts['fqdn'] = '%s.%s' % (wiz.opts['hostname'], wiz.opts['domain'])
    if 'realm' not in wiz.opts:
        wiz.opts['realm'] = wiz.opts['domain'].upper()
    if 'kdc' not in wiz.opts:
        wiz.opts['kdc'] = 'kerberos.' + wiz.opts['domain']
    if 'kadmin' not in wiz.opts:
        wiz.opts['kadmin'] = 'kerberos.' + wiz.opts['domain']
    if 'auto_update' not in wiz.opts:
        wiz.opts['auto_update'] = True

@feature('client')
def client_nss_stop(wiz):
    for s in ['tnscd', 'nscd']:
        service.service_stop(s)

@feature('client')
def client_krb5conf(wiz):
    cfg = Krb5Conf()
    cfg.setRealmDomain(wiz.opts['realm'], wiz.opts['domain'])
    cfg.setRealm(wiz.opts['realm'], wiz.opts['kdc'], wiz.opts['kadmin'])
    cfg.setDefaultRealm(wiz.opts['realm'])
    cfg.setPamConfig()
    cfg.save()

@feature('client')
def client_makeconf(wiz):
    if not os.path.exists('/etc/Tartarus/clients'):
        os.makedirs('/etc/Tartarus/clients')
    config.gen_config_from_file('/etc/Tartarus/clients/common.conf',
                                _all_template, wiz.opts, True)
    old_conf_path = '/etc/Tartarus/clients/all.config'
    if os.path.exists(old_conf_path): os.unlink(old_conf_path)
    os.symlink('common.conf', old_conf_path)

@feature('client')
def client_comm_init(wiz):
    wiz.comm, _ = initialize()

@feature('client')
def client_kinit(wiz):
    admin = wiz.dialog.ask('Tartarus domain administrator login:', 'sysadmin')
    krb5user.kinitPasswordPromptPosix(admin)
    spn = 'host/%s' % wiz.opts['fqdn']
    krb5prx = wiz.comm.propertyToProxy('Tartarus.Kerberos.KadminPrx')
    kadmin = Kerberos.KadminPrx.checkedCast(krb5prx)
    try:
        spr = kadmin.createServicePrincipal('host', wiz.opts['fqdn'])
    except core.AlreadyExistsError:
        spr = kadmin.getPrincKeys(spn)
    save_keys(spr)

@feature('client')
def client_dnsupdate(wiz):
    service.service_restart('tdnsupdate')
    if wiz.opts['auto_update']:
        service.service_on('tdnsupdate')
    else:
        service.service_off('tdnsupdate')

@feature('client')
def client_dhcpreg(wiz):
    os.rename('/etc/dhcpcd.conf', '/etc/dhcpcd.conf.tsave')
    with open('/etc/dhcpcd.conf', 'w+') as f:
        set = False
        for line in open('/etc/dhcpcd.conf.tsave'):
            if line.startswith('clientid'):
                f.write('clientid %s\n' % wiz.opts['hostname'])
                set = True
            else:
                f.write(line)
        if not set:
            f.write('clientid %s\n' % wiz.opts['hostname'])
    prx = wiz.comm.stringToProxy('DHCP/Server')
    prx = DHCP.ServerPrx.checkedCast(prx)
    if not prx: raise RuntimeError('Can\'t connect to server')
    srv = DHCP.ServerPrx.checkedCast(prx)
    srv.addHost(wiz.opts['hostname'], DHCP.HostId(DHCP.HostIdType.IDENTITY, wiz.opts['hostname']))

@feature('client')
def client_nss_start(wiz):
    for s in ['tnscd', 'nscd']:
        service.service_start(s)
        service.service_on(s)

@feature('client')
def client_netauth(wiz):
    pam.set_tartarus_auth()

