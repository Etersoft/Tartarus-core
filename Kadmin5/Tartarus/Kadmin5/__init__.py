
import Tartarus, KadminI

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

    adapter.add(KadminI.KadminI(d > 0), c.stringToIdentity("Kadmin5"))

