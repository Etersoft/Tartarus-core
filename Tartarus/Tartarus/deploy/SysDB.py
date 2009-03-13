import sys
import re

import Tartarus
from common import _checked_configure
from Tartarus.iface import SysDB
from Tartarus.deploy.common import feature, after, before

@feature('sysdb')
@after('service_init')
@before('service_checks_done')
def sysdb_checks(wiz):
    wiz.dialog.info('Checking for SysDB...')
    prx = wiz.comm.propertyToProxy("Tartarus.deployPrx.SysDBService")
    try:
        s = Tartarus.iface.core.ServicePrx.checkedCast(prx)
    except:
        return 'SysDB service not found. It may be not to be installed.'
    if not s:
        return 'SysDB service not found. It may be not to be installed.'
    if s.isConfigured():
        prompt = "SysDB configuration already exists. Force reinitialization?"
        if not wiz.dialog.force(prompt):
            return 'Deployment canceled'
    wiz.sysdb_service = s

@feature('sysdb')
@after('sysdb_checks', 'service_checks_done')
@before('service_dialog_done')
def sysdb_dialog(wiz):
    if 'users' in wiz.opts: return
    users = []
    add = lambda name, full_name, password, is_adm: users.append((name, full_name, password, is_adm))
    name = _ask_user('User name for system administrator', 'sysadmin', wiz)
    password = wiz.dialog.password('Enter password for system administrator.')
    add(name, 'System administrator', password, True)
    msg = 'Do you want create user new account for Tartarus?'
    while wiz.dialog.yesno(msg, False):
        name = _ask_user('Enter new user login name', None, wiz)
        full_name = _ask_user('Enter new user full name', name, wiz)
        password = wiz.dialog.password('Enter password for %s user.' % name, min_len=5)
        add(name, full_name, password, False)
    wiz.opts['users'] = users

@feature('sysdb')
@after('sysdb_dialog', 'service_dialog_done', 'server_nss_stop')
@before('service_restart', 'server_nss_start')
def sysdb_deploy(wiz):
    wiz.dialog.info('Configuring SysDB...')

    wiz.sysdb_service.configure({'force': 'force'})
    prx = wiz.comm.propertyToProxy('Tartarus.deployPrx.UserManager')
    um = SysDB.UserManagerPrx.checkedCast(prx)
    prx = wiz.comm.propertyToProxy('Tartarus.deployPrx.GroupManager')
    gm = SysDB.GroupManagerPrx.checkedCast(prx)

    admins_gid = gm.create(SysDB.GroupRecord(-1, "netadmins",
                                             "Network administrators"))
    users_gid = gm.create(SysDB.GroupRecord(-1, "netusers", "Network users"))

    for name, full_name, _, is_adm in wiz.opts['users']:
        if is_adm:
            uid = um.create(SysDB.UserRecord(-1, admins_gid, name, full_name))
            gm.addUsers(users_gid, [uid])
        else:
            um.create(SysDB.UserRecord(-1, users_gid, name, full_name))

def deploy_sysdb(comm, opts):
    """Put inital data to SysDB.

    @param comm
      a communicator. The following proxies should be available:
        - Tartarus.deployPrx.UserManager of type Tartarus::SysDB::UserManager
        - Tartarus.deployPrx.GroupManager of type Tartarus::SysDB::GroupManager
        - Tartarys.deployPrx.SysDBService of type Tartarus::core::Service
    @param opts
      a dictionary { option name : option value }. The following options are used
          *Name* *Type* *Madatory* *Comment*
          name   String M          n/a
    """
    prx = comm.propertyToProxy('Tartarus.deployPrx.SysDBService')
    _checked_configure(prx, opts.get('sysdb_force'))

    prx = comm.propertyToProxy('Tartarus.deployPrx.UserManager')
    um = SysDB.UserManagerPrx.checkedCast(prx)
    prx = comm.propertyToProxy('Tartarus.deployPrx.GroupManager')
    gm = SysDB.GroupManagerPrx.checkedCast(prx)

    admins_gid = gm.create(SysDB.GroupRecord(-1, "netadmins",
                                             "Network administrators"))
    users_gid = gm.create(SysDB.GroupRecord(-1, "netusers", "Network users"))

    uid = um.create(SysDB.UserRecord(-1, admins_gid, opts['name'],
                                     "System administrator"))
    gm.addUsers(users_gid, [uid])

GOOD_USER_NAME = "[A-Za-z]\w{2,30}$"

def _ask_user(prompt, default, wiz):
    good_name = re.compile(GOOD_USER_NAME)
    while True:
        ans = wiz.dialog.ask(prompt, default)
        if not good_name.match(ans):
            print 'User name should match ' + repr(GOOD_USER_NAME)
            continue
        return ans

