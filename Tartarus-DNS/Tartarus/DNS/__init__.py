
import db, server, zone

def init(adapter):
    com = adapter.getCommunicator()
    db.init(com.getProperties())

    adapter.add(server.ServerI(),
            com.stringToIdentity("DNS-Server/Server"))
    adapter.addServantLocator(zone.Locator(), "DNS-Zone")
