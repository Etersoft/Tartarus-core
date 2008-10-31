
import traceback, sys, os, Ice, Tartarus


Tartarus.modules.trace = 0
Tartarus.slices.trace = 0
Tartarus.slices.path = ["../../slice"]

def run(test, args):
    try:
        com = Ice.initialize(args)
        try:
            pr = com.propertyToProxy("Tartarus.DNS.Prx")
            DNS = Tartarus.iface.DNS
            s = DNS.ServerPrx.checkedCast(pr)
            test(com,s)
        finally:
            com.destroy()
        return 0
    except:
        traceback.print_exc()
        return -1

def main():
    (p, f) = os.path.split(sys.argv[1])
    (m, e) = os.path.splitext(f)
    sys.path.append(p)
    __import__(m)
    mod = sys.modules[m]
    sys.exit(run(mod.test, sys.argv[2:]))

if __name__ == '__main__':
    main()

