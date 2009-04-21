from Tartarus import system
from Tartarus.deploy.common import feature, after, before
from Tartarus.deploy.client import client_nss_stop, client_makeconf, client_nss_start, client_netauth

@feature('server')
@after('service_init')
def server_nss_stop(wiz):
    client_nss_stop(wiz)

@feature('server')
def server_domain(wiz):
    domain = system.hostname.getdomain()
    if 'domain' in wiz.opts:
        domain = wiz.opts.pop('domain')
    if not wiz.dialog.yesno("This utility will deploy "
                            "Tartarus domain for this server\n"
                            "Domain name: [%s]\n"
                            "Do you want to proceed?"
                            % domain):
        return 'Aborted.'
    # Must contain '.' as domain name, start with valid symbols,
    # and not have intersections with localhost.localdomain domain
    # (TODO: check it properly)
    if domain.find('.') < 0 or len(domain) < 2 or domain.endswith('.localdomain') or domain.endswith('.localdomain.'):
        return "Can\'t deploy in to \'%s\' domain.\n" \
               "Please check your network instalation.\n" \
               "Aborted." % domain
    wiz.opts['domain'] = domain

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

