
import Tartarus
from Tartarus.iface import core as C

def _checked_configure(svc_proxy, force, params = None):
    if not params:
        params = {}
    if not svc_proxy:
        raise C.RuntimeError('Proxy not found')

    svc = C.ServicePrx.checkedCast(svc_proxy)
    if not svc:
        raise C.RuntimeError('Wrong service proxy')

    if svc.isConfigured() and not force:
        raise C.RuntimeError('Database already exists')
    params['force'] = force
    svc.configure(params)

