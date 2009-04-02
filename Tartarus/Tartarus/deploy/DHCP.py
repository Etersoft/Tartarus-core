import sys
import re

from Tartarus.iface import DHCP
from Tartarus.deploy.common import feature, after, before
from Tartarus import system
from Tartarus.system.ipaddr import IpSubnet, IpRange

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
    subnets = []
    for addr, mask in system.hostname.getsystemnets():
        mask = mask or 24
        subnet = IpSubnet('%s/%s' % (addr, mask))
        if wiz.dialog.yesno('Do you want add subnet %s do DHCP?' % subnet.cidr):
            range = _ask_range(wiz, subnet)
            subnets.append((subnet, range))
    wiz.opts['dhcp_subnets'] = subnets

_range_re = re.compile('^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}-\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$')

def _ask_range(wiz, subnet):
    start = subnet.start.int + 10
    end = subnet.start.int + 100
    if end > subnet.end.int: end = subnet.end.int - 1
    range = IpRange(start, end)
    default_range = '%s-%s' % (range.start.str, range.end.str)
    while True:
        ask = 'Range used for dynamic address allocation in %s subnet' % subnet.cidr
        answer = wiz.dialog.ask(ask, default_range)
        if not _range_re.match(answer):
            wiz.dialog.error('Wrong value for IP range')
            continue
        start, end = answer.split('-')
        range = IpRange(start, end)
        if range not in subnet:
            wiz.dialog.error('"%s" range not in %s subnet' % (answer, subnet.cidr))
            continue
        return range

@feature('dhcp')
@after('dhcp_dialog', 'service_dialog_done')
@before('service_restart')
def dhcp_deploy(wiz):
    wiz.dialog.info('Configuring DHCP...')
    prx = wiz.comm.stringToProxy('DHCP/Server')
    srv = DHCP.ServerPrx.checkedCast(prx)
    srv.reset()
    if len(wiz.opts['dhcp_subnets']) == 0: return
    for subnet, range in wiz.opts['dhcp_subnets']:
        sbn = srv.addSubnet(subnet.cidr)
        sbn.addRange(range.start.str, range.end.str, 3)
    prx = wiz.comm.stringToProxy('DHCP/Daemon')
    daemon = DHCP.DaemonPrx.checkedCast(prx)
    if daemon.running():
        daemon.stop()
    daemon.start()

