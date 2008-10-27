
import user
import Tartarus, Ice
Tartarus.slices.path=['../slice', '/usr/share/Tartarus/slice']
import Tartarus.iface.Kadmin5 as I

c = Ice.initialize()
a = I.KadminPrx.checkedCast(c.propertyToProxy("Tartarus.Kadmin5.Prx"))


