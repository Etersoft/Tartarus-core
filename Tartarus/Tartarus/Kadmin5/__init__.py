
import Tartarus
import KadminI, kdb

from Tartarus import logging

#
# Initialize the servants
# see README file for more information
#
def init(adapter):
    c = adapter.getCommunicator()
    logging.trace("Tartarus.Kadmin5", "Initializing...",
            log_to = c, cond = "Tartarus.Kadmin5.trace")
    d = c.getProperties().getPropertyAsInt('Tartarus.Kadmin5.deploy')

    kdb_common = kdb.Kdb(d)

    adapter.add(kdb.KadminService(kdb_common),
                c.stringToIdentity("Service/Kerberos"))
    adapter.add(KadminI.KadminI(kdb_common),
                c.stringToIdentity("Kerberos/Kadmin"))

