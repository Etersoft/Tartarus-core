
import users, groups
from Tartarus import db
from Tartarus.iface import SysDB as I

def init(adapter):
    try:
        com = adapter.getCommunicator()
        props = com.getProperties()

        prefix = 'Tartarus.SysDB.db.' # with terminating dot!
        dbh = db.make_helper(props.getPropertiesForPrefix(prefix), prefix, I)

        uo = props.getPropertyAsIntWithDefault(
                "Tartarus.SysDB.UserIDOffset", 65536)
        go = props.getPropertyAsIntWithDefault(
                "Tartarus.SysDB.GroupIDOffset", 65536)
        adapter.add(users.UserManagerI(dbh, uo, go),
                com.stringToIdentity("SysDB-Mangager/Users"))
        adapter.add(groups.GroupManagerI(dbh, uo, go),
                com.stringToIdentity("SysDB-Mangager/Groups"))
    except:
        import traceback
        traceback.print_exc()


