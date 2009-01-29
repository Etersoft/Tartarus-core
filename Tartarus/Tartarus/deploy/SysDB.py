
import Tartarus
from common import _checked_configure
from Tartarus.iface import SysDB

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

