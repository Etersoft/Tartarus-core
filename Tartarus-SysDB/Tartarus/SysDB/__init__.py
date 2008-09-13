
import users, groups, deploy
from Tartarus import db
from Tartarus.iface import SysDB as I

def init(adapter):
    com = adapter.getCommunicator()
    props = com.getProperties()

    prefix = 'Tartarus.SysDB.db.' # with terminating dot!
    dbh = db.make_helper(props.getPropertiesForPrefix(prefix), prefix, I)

    if props.getPropertyAsInt(prefix + 'deploy') > 0:
        deploy.create_db(dbh)

    #check that database parameters are valid
    try:
        dbh.get_connection()
    except dbh.Error, e:
        raise I.DBError("Could not connect to database", e.message)

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

