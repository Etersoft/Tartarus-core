
import sys, os, Ice, Tartarus
import Tartarus.iface.SysDB as I

def deploy(com):
    um = com.propertyToProxy("Tartarus.SysDB.UserManagerPrx")
    if not um:
        raise I.ConfigError("Could not locate user manager",
                "Tartarus.SysDB.UserManagerPrx")
    gm = com.propertyToProxy("Tartarus.SysDB.GroupManagerPrx")
    if not gm:
        raise I.ConfigError("Could not locate user manager",
                "Tartarus.SysDB.GroupManagerPrx")

    um = I.UserManagerPrx.checkedCast(um)
    if not um:
        raise I.ConfigError("Could not connect to user manager",
                "Tartarus.SysDB.UserManagerPrx")
    gm = I.GroupManagerPrx.checkedCast(gm)
    if not gm:
        raise I.ConfigError("Could not connect to group manager",
                "Tartarus.SysDB.GroupManagerPrx")

    admins_gid = gm.create(I.GroupRecord(-1, "admins", "System administartors"))
    users_gid = gm.create(I.GroupRecord(-1, "users", "Users"))

    uid = um.create(I.UserRecord(-1, admins_gid, "admin", "System administrator"))
    gm.addUsers(users_gid, [uid])

def main():
    class App(Ice.Application):
        def run(self, args):
            try:
                if os.path.isfile("./deploy.conf"):
                    self.communicator().getProperties().load("./deploy.conf")
                deploy(self.communicator())
            except I.ConfigError, e:
                logging.error('SysDB: %s: %s' % (e.message, e.property))
                return -1
            except I.Error, e:
                logging.error('SysDB: ' + e.message)
                return -1
    return App().main(sys.argv)

if __name__ == '__main__':
    main()


