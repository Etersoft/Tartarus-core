
import os
from Tartarus.system import config, service, pam

_all_template = '/usr/share/Tartarus/templates/all/common.config.template'


def deploy_client_start(opts):
    for s in ['tnscd', 'nscd']:
        service.service_stop(s)
    if not os.path.exists('/etc/Tartarus/clients'):
        os.makedirs('/etc/Tartarus/clients')
    config.gen_config_from_file('/etc/Tartarus/clients/common.config',
                                _all_template, opts, True)
    os.symlink('common.config', '/etc/Tartarus/clients/all.config')

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
