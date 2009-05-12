
import Tartarus
import TimeI, service

from Tartarus import logging, auth

#
# Initialize the servants
# see README file for more information
#
def init(adapter):
    c = adapter.getCommunicator()
    logging.trace("Tartarus.Time", "Initializing...",
            log_to = c, cond = "Tartarus.Time.trace")
    #d = c.getProperties().getPropertyAsInt('Tartarus.Time.deploy')

    adapter.add(service.service(),
                c.stringToIdentity("Service/Time"))
    loc = auth.SrvLocator()
    loc.add_object(TimeI.TimeI(),
                   c.stringToIdentity("Time/Server"))
    adapter.addServantLocator(loc, "Time")

