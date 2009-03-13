from Tartarus import system
from Tartarus.deploy.common import feature, after, before
from Tartarus.deploy.client import client_nss_stop, client_makeconf, client_nss_start, client_netauth

@feature('server')
@after('service_init')
def server_nss_stop(wiz):
    client_nss_stop(wiz)

@feature('server')
def server_domain(wiz):
    if 'domain' in wiz.opts: return
    wiz.opts['domain'] = system.hostname.getdomain()
    if not wiz.dialog.yesno("This utility will deploy "
                            "Tartarus domain for this server\n"
                            "Domain name: %s\n"
                            "Do you want to proceed?"
                            % wiz.opts['domain']):
        return 'Aborted.'

@feature('server')
@after('service_checks_done')
def server_makeconf(wiz):
    client_makeconf(wiz)

@feature('server')
@after('server_makeconf')
def server_nss_start(wiz):
    client_nss_start(wiz)

@feature('server')
@after('server_nssstart')
def server_netauth(wiz):
    client_netauth(wiz)

