from network import ServerI, DaemonI, Saver, SubnetLocator, HostLocator, Daemon
from server import Server

def init(adapter):
    com = adapter.getCommunicator()
    props = com.getProperties()

    cfg_fname = props.getPropertyWithDefault(
            'Tartarus.DHCP.ConfigFile', '/usr/share/Tartarus/dhcp/dhcpd.conf')
    dhcp_cfg_fname = props.getPropertyWithDefault(
            'Tartarus.DHCP.DHCPConfigFile', '/etc/dhcp/dhcpd.conf')

    Saver(cfg_fname, dhcp_cfg_fname).load()
    server = Server.get()
    if server.startOnLoad():
        Daemon.get().start()

    ident = com.stringToIdentity('DHCP/Server')
    adapter.add(ServerI(), ident)
    ident = com.stringToIdentity('DHCP/Daemon')
    adapter.add(DaemonI(), ident)

    adapter.addServantLocator(SubnetLocator(), "DHCP-Subnets")
    adapter.addServantLocator(HostLocator(), "DHCP-Hosts")

