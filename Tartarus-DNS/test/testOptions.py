
import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    for opt in server.getOptions():
        print "%s=%s" % (opt.name, opt.value)
    server.changeOptions([DNS.ServerOption('recursor', '192.168.33.1')])
    for opt in server.getOptions():
        print "%s=%s" % (opt.name, opt.value)

    server.changeOptions([DNS.ServerOption('recursor', '')])
    for opt in server.getOptions():
        print "%s=%s" % (opt.name, opt.value)


