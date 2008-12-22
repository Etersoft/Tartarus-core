
import users, groups, deploy
from Tartarus import db, auth
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

    adm_groups = props.getProperty('Tartarus.SysDB.Auth.AdminGroups').split()
    if len(adm_groups) > 0:
        import authorize
        auth.set_default(authorize.SimpleGroupAuthorizer(dbh, adm_groups))
    else:
        auth.set_default(lambda x_, y_: True)

    loc = auth.SrvLocator()
    loc.add_object(users.UserManagerI(dbh, uo, go),
            com.stringToIdentity("SysDB-Manager/Users"))
    loc.add_object(groups.GroupManagerI(dbh, uo, go),
            com.stringToIdentity("SysDB-Manager/Groups"))
    adapter.addServantLocator(loc, "SysDB-Manager")

    vname = props.getProperty('Tartarus.SysDB.SSLVerifier')
    if len(vname) > 0:
        import sslverify
        sslverify.setup(com, dbh, vname, props)

