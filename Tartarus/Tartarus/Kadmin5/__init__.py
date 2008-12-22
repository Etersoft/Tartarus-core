
import Tartarus
import KadminI, kdb

from Tartarus import logging, auth

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
    loc = auth.SrvLocator()
    loc.add_object(KadminI.KadminI(kdb_common),
                   c.stringToIdentity("Kerberos/Kadmin"))
    adapter.addServantLocator(loc, "Kerberos")

