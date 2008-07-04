
import traceback, sys, os, Ice, Tartarus


Tartarus.modules.trace = 0
Tartarus.slices.trace = 0
Tartarus.slices.path += ["../slice"]

def run(test, args):
    try:
        com = Ice.initialize(args)
        try:
            SysDB = Tartarus.iface.SysDB
            pr = com.propertyToProxy("Tartarus.SysDB.UserManagerPrx")
            um = SysDB.UserManagerPrx.checkedCast(pr)
            pr = com.propertyToProxy("Tartarus.SysDB.GroupManagerPrx")
            gm = SysDB.GroupManagerPrx.checkedCast(pr)
            test(com,um, gm)
        finally:
            com.destroy()
        return 0
    except:
        traceback.print_exc()
        return -1

def main():
    if len(sys.argv) != 2 or len(sys.argv[1]) == 0:
        print 'Usage: %s <test>' % sys.argv[0]
    (p, f) = os.path.split(sys.argv[1])
    (m, e) = os.path.splitext(f)
    sys.path.append(p)
    __import__(m)
    mod = sys.modules[m]
    sys.exit(run(mod.test, sys.argv[2:]))

if __name__ == '__main__':
    main()

