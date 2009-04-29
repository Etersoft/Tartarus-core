from __future__ import with_statement
import os
from Tartarus.system import config, service, pam
from Tartarus.deploy.common import feature, after, before

@feature('leave')
def client_leave(wiz):
    for s in ['tnscd', 'nscd']:
        try:
            service.service_stop(s)
            service.service_off(s)
        except service.ServiceNotFound:
            pass
    pam.set_local_auth()
