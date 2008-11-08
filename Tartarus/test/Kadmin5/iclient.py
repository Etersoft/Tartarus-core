
import user
import Tartarus, Ice
Tartarus.slices.path=['../../slice']
import Tartarus.iface.Kerberos as I

c = Ice.initialize()
a = I.KadminPrx.checkedCast(c.propertyToProxy("Tartarus.Kadmin.Prx"))


