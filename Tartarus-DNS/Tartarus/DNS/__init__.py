
import server, zone, deploy
from Tartarus import db
from Tartarus.iface import DNS as I

def init(adapter):
    com = adapter.getCommunicator()
    props = com.getProperties()

    cfg_file_name = props.getPropertyWithDefault(
            'Tartarus.DNS.ConfigFile', '/etc/powerdns/pdns.conf')

    prefix = 'Tartarus.DNS.db.' # with terminating dot!
    dbh = db.make_helper(props.getPropertiesForPrefix(prefix), prefix, I)

    do_reload = True

    if props.getPropertyAsInt('Tartarus.DNS.db.deploy') > 0:
        deploy.do_deploy(dbh, cfg_file_name)
        do_reload = False

    #minimal test whether configuration works
    dbh.get_connection()

    adapter.add(server.ServerI(cfg_file_name, dbh, do_reload),
            com.stringToIdentity("DNS-Server/Server"))
    adapter.addServantLocator(zone.Locator(dbh), "DNS-Zone")

