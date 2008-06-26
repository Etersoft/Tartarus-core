
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
    adapter.add(KadminI.KadminI(), c.stringToIdentity("Kadmin5"))

