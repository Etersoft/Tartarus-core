
import os
from Tartarus.system import config, service, pam

_all_template = '/usr/share/Tartarus/templates/clients/all.config.template'


def deploy_client_start(opts):
    if not os.path.exists('/etc/Tartarus/clients'):
        os.makedirs('/etc/Tartarus/clients')
    config.gen_config_from_file('/etc/Tartarus/clients/all.config',
                                _all_template, opts, True)

def deploy_client_finish(opts_):
    service.service_start('tnscd')
    service.service_on('tnscd')
    pam.set_tartarus_auth()

def deploy_client_for_server(opts):
    deploy_client_start(opts)
    for s in ['krb5kdc', 'powerdns', 'Tartarus']:
        service.service_restart(s)
    deploy_client_finish(opts)
