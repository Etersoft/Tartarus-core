
import os
from Tartarus.system import config, service, pam
import Tartarus.system.resolv as resolv
from Tartarus.deploy.common import feature, after, before

_all_template = '/usr/share/Tartarus/templates/all/common.conf.template'

@feature('client')
def client_nss_stop(wiz):
    for s in ['tnscd', 'nscd']:
        service.service_stop(s)

@feature('client')
def client_dialog(wiz):
    if 'fqdn' not in q.answers:
        domain = Tartarus.system.hostname.getdomain()
        fqdn = get_checked_fqdn(domain, Tartarus.system.hostname.getfqdn())
        fqdn_list.append(fqdn)

        localhosts = hosts.get_localhosts()
        for record in localhosts:
            for h in record.split():
                if not h.startswith('localhost') and h.find('.') > 0:
                    fqdn_list.append(h) 

        user_fqdn = consdialog.choice(
                'Enter Full Qualified Domain Name (FQDN) of your host', fqdn_list)
        if user_fqdn != fqdn:
            domain = Tartarus.system.hostname.getdomain(user_fqdn)
            fqdn = get_checked_fqdn(domain, user_fqdn)
            Tartarus.system.hostname.sethostname(fqdn)
            q.answers['fqdn'] = fqdn
    if 'domain' not in q.answers:
        domain = system.hostname.getdomain(q.answers['fqdn'])
        q.answers['domain'] = domain


@feature('client')
@after('client_stop_services')
def client_makeconf(wiz):
    if not os.path.exists('/etc/Tartarus/clients'):
        os.makedirs('/etc/Tartarus/clients')
    config.gen_config_from_file('/etc/Tartarus/clients/common.conf',
                                _all_template, wiz.opts, True)
    old_conf_path = '/etc/Tartarus/clients/all.config'
    if os.path.exists(old_conf_path): os.unlink(old_conf_path)
    os.symlink('common.conf', old_conf_path)

@feature('client')
def client_dnsupdate(wiz):
    service.service_restart('tdnsupdate')
    if auto_update:
        service.service_on('tdnsupdate')
    else:
        service.service_off('tdnsupdate')

@feature('client')
def client_nss_start(wiz):
    for s in ['tnscd', 'nscd']:
        service.service_start(s)
        service.service_on(s)

@feature('client')
def client_netauth(wiz):
    pam.set_tartarus_auth()

def deploy_client_start(opts):
    for s in ['tnscd', 'nscd']:
        service.service_stop(s)
    if not os.path.exists('/etc/Tartarus/clients'):
        os.makedirs('/etc/Tartarus/clients')
    config.gen_config_from_file('/etc/Tartarus/clients/common.conf',
                                _all_template, opts, True)
    old_conf_path = '/etc/Tartarus/clients/all.config'
    if os.path.exists(old_conf_path): os.unlink(old_conf_path)
    os.symlink('common.conf', old_conf_path)

def deploy_client_dnsupdate(opts_, auto_update = False):
    service.service_restart('tdnsupdate')
    if auto_update:
        service.service_on('tdnsupdate')
    else:
        service.service_off('tdnsupdate')

def deploy_client_finish(opts_):
    for s in ['tnscd', 'nscd']:
        service.service_restart(s)
        service.service_on(s)
    pam.set_tartarus_auth()

def deploy_server_pre():
    service.tartarus_start_deploy()

def deploy_server_start(opts):
    deploy_client_start(opts)

def deploy_server_stop(opts):
    for s in ['krb5kdc', 'kadmin', 'powerdns', 'Tartarus']:
        service.service_on(s)
        service.service_restart(s)
    deploy_client_finish(opts)

def leave_client(opts_):
    for s in ['tnscd', 'nscd']:
        service.service_off(s)
        service.service_stop(s)
    pam.set_local_auth()

