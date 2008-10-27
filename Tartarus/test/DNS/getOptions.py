
import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    for opt in server.getOptions():
        print "%s=%s" % (opt.name, opt.value)


