import sys

from Tartarus.iface import DHCP
from Tartarus.deploy.common import feature, after, before
from Tartarus import system
from socket import inet_aton, inet_ntoa
from struct import pack, unpack

@feature('dhcp')
@before('service_checks_done')
def dhcp_checks(wiz):
    wiz.dialog.info('Checking for DHCP...')
    prx = wiz.comm.stringToProxy('DHCP/Server')
    try:
        srv = DHCP.ServerPrx.checkedCast(prx)
    except:
        return 'DHCP service not found. It may be not to be installed.'
    if not srv:
        return 'DHCP service not found. It may be not to be installed.'
    if srv.isConfigured():
        prompt = "DHCP configuration already exists. Force reinitialization?"
        if not wiz.dialog.force(prompt):
            return 'Deployment canceled'
    wiz.dhcp_server = srv

@feature('dhcp')
@after('dhcp_checks', 'service_checks_done')
@before('service_dialog_done')
def dhcp_dialog(wiz):
    dhcp_subnets = []
    add = lambda decl, range: dhcp_subnets.append((decl, range))
    for addr, mask in system.hostname.getsystemnets():
        mask = mask or 24
        decl, range = _calc(addr, int(mask))
        if wiz.dialog.yesno('Do you want add subnet %s do DHCP?' % decl):
            range = wiz.dialog.ask('Range used for dynamic address allocation', range)
            add(decl, range)
    wiz.opts['dhcp_subnets'] = dhcp_subnets

def _calc(addr, mask):
    b = 32 - mask
    if 2**b < 256: return None
    addr = IpAddr.s2i(addr)
    addr = (addr >> b) << b
    start = IpAddr.i2s(addr + 10)
    end = IpAddr.i2s(addr + 100)
    addr = IpAddr.i2s(addr) 
    return '%s/%d' % (addr, mask), '%s-%s' % (start, end)

class IpAddr:
    @staticmethod
    def i2s(addr):
        return inet_ntoa(pack('>I', addr))
    @staticmethod
    def s2i(addr):
        return unpack('>I', inet_aton(addr))[0]

@feature('dhcp')
@after('dhcp_dialog', 'service_dialog_done')
@before('service_restart')
def dhcp_deploy(wiz):
    wiz.dialog.info('Configuring DHCP...')
    prx = wiz.comm.stringToProxy('DHCP/Server')
    srv = DHCP.ServerPrx.checkedCast(prx)
    srv.reset()
    srv.commit()
    if len(wiz.opts['dhcp_subnets']) == 0: return
    for decl, range in wiz.opts['dhcp_subnets']:
        sbn = srv.addSubnet(decl)
        _set_range(sbn, DHCP.RangeType.UNTRUST, range)
    srv.commit()
    prx = wiz.comm.stringToProxy('DHCP/Daemon')
    daemon = DHCP.DaemonPrx.checkedCast(prx)
    if daemon.running():
        daemon.stop()
    daemon.start()
    srv.commit()

def _set_range(sbn, type, rdef):
    if rdef:
        start, end = rdef.split('-')
        range = DHCP.IpRange(start, end, True)
        sbn.setRange(type, range)

