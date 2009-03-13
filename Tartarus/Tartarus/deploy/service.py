import os

from Tartarus.deploy.common import feature, after, before
from Tartarus.system import config, service, pam

@feature('service')
def service_init(wiz):
    if os.getuid() != 0:
        return 'Only root can do this'
    service.tartarus_start_deploy()

@feature('service')
@after('service_init')
def service_checks_done(wiz):
    pass

@feature('service')
@after('service_checks_done')
def service_dialog_done(wiz):
    pass

@feature('service')
@after('service_deploy_done')
def service_restart(wiz):
    wiz.comm.destroy()
    service.service_restart('Tartarus')
    service.service_on('Tartarus')

