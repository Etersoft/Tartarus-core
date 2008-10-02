
import users, groups, deploy
from Tartarus import db
from Tartarus.iface import SysDB as I

def init(adapter):
    com = adapter.getCommunicator()
    props = com.getProperties()

    prefix = 'Tartarus.SysDB.db.' # with terminating dot!
    dbh = db.make_helper(props.getPropertiesForPrefix(prefix), prefix)

    enable_deploy = props.getPropertyAsInt(prefix + 'deploy') > 0
    adapter.add(deploy.SysDBService(dbh, enable_deploy),
            com.stringToIdentity('Service/SysDB'))

    uo = props.getPropertyAsIntWithDefault(
            "Tartarus.SysDB.UserIDOffset", 65536)
    go = props.getPropertyAsIntWithDefault(
            "Tartarus.SysDB.GroupIDOffset", 65536)
    adapter.add(users.UserManagerI(dbh, uo, go),
            com.stringToIdentity("SysDB-Manager/Users"))
    adapter.add(groups.GroupManagerI(dbh, uo, go),
            com.stringToIdentity("SysDB-Manager/Groups"))

    vname = props.getProperty('Tartarus.SysDB.SSLVerifier')
    if len(vname) > 0:
        import sslverify
        sslverify.setup(com, dbh, vname, props)

