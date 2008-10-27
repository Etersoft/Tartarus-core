
import server, zone, deploy
from Tartarus import db
from Tartarus.iface import DNS as I

def init(adapter):
    com = adapter.getCommunicator()
    props = com.getProperties()

    cfg_file_name = props.getPropertyWithDefault(
            'Tartarus.DNS.ConfigFile', '/etc/powerdns/pdns.conf')

    prefix = 'Tartarus.DNS.db.' # with terminating dot!
    dbh = db.make_helper(props.getPropertiesForPrefix(prefix), prefix)

    do_reload = True

    enable_deploy =  props.getPropertyAsInt('Tartarus.DNS.db.deploy') > 0
    if enable_deploy:
        do_reload = False

    adapter.add(deploy.DNSService(dbh, cfg_file_name, enable_deploy),
            com.stringToIdentity('Service/DNS'))

    #minimal test whether configuration works
    dbh.get_connection()

    adapter.add(server.ServerI(cfg_file_name, dbh, do_reload),
            com.stringToIdentity("DNS-Server/Server"))
    adapter.addServantLocator(zone.Locator(dbh), "DNS-Zone")

