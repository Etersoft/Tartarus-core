
import os
from Tartarus.system import config, service, pam

_all_template = '/usr/share/Tartarus/templates/clients/all.config.template'


def deploy_client_start(opts):
    service.service_stop('tnscd')
    if not os.path.exists('/etc/Tartarus/clients'):
        os.makedirs('/etc/Tartarus/clients')
    config.gen_config_from_file('/etc/Tartarus/clients/all.config',
                                _all_template, opts, True)

def deploy_client_dnsupdate(opts_, auto_update = False):
    service.service_restart('tdnsupdate')
    if auto_update:
        service.service_on('tdnsupdate')

def deploy_client_finish(opts_):
    service.service_start('tnscd')
    service.service_on('tnscd')
    pam.set_tartarus_auth()

def deploy_client_for_server(opts):
    deploy_client_start(opts)
    for s in ['krb5kdc', 'powerdns', 'Tartarus']:
        service.service_restart(s)
    deploy_client_finish(opts)

def leave_client(opts_):
    service.service_off('tnscd')
    service.service_stop('tnscd')
    pam.set_local_auth()
