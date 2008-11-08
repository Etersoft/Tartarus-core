
import Ice, kadmin5, sys, Tartarus

import Tartarus.iface.Kerberos as I

c = Ice.initialize()
a = I.KadminPrx.checkedCast(c.propertyToProxy("Tartarus.Kadmin5.Prx"))

t = kadmin5.keytab()

try:
    svc = sys.argv[1]
except IndexError:
    svc = "host"

try:
    hostname = sys.argv[2]
except IndexError:
    from socket import getfqdn
    hostname = getfqdn()

pr = a.createServicePrincipal(svc, hostname)

for k in pr.keys:
    t.add_entry(pr.name, k.kvno, k.enctype, k.data)

