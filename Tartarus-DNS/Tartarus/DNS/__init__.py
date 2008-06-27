
import server, zone
from Tartarus import db
from Tartarus.iface import DNS as I

def init(adapter):
    com = adapter.getCommunicator()
    props = com.getProperties()

    cfg_file_name = props.getPropertyWithDefault(
            'Tartarus.DNS.ConfigFile', '/etc/powerdns/pdns.conf')

    prefix = 'Tartarus.DNS.db.' # with terminating dot!
    dbh = db.make_helper(props.getPropertiesForPrefix(prefix), prefix, I)
    adapter.add(server.ServerI(cfg_file_name, dbh),
            com.stringToIdentity("DNS-Server/Server"))
    adapter.addServantLocator(zone.Locator(dbh), "DNS-Zone")

