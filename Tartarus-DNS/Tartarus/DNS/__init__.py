
import db, server, zone

def init(adapter):
    com = adapter.getCommunicator()
    props = com.getProperties()
    db.init(props)

    cfg_file_name = props.getPropertyWithDefault(
            'Tartarus.DNS.ConfigFile', '/etc/powerdns/pdns.conf')

    adapter.add(server.ServerI(cfg_file_name),
            com.stringToIdentity("DNS-Server/Server"))
    adapter.addServantLocator(zone.Locator(), "DNS-Zone")

