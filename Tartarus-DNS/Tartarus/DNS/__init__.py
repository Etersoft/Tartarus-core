
import db, server,domain

def init(adapter):
    com = adapter.getCommunicator()
    db.init(com.getProperties())

    adapter.add(server.ServerI(),
            com.stringToIdentity("DNS-Server/Server"))
    adapter.addServantLocator(domain.Locator(),
            "DNS-Domain")
