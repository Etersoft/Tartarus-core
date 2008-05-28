
import rlcompleter
import readline
readline.parse_and_bind("tab: complete")



import Tartarus, Ice


import Tartarus.iface.Kadmin5 as I

c = Ice.initialize()
a = I.KadminPrx.checkedCast(c.propertyToProxy("Tartarus.Kadmin5.Prx"))


