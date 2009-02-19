from network import ServerI, DaemonI, SubnetLocator, HostLocator, Daemon
from server import Server
import options

def init(adapter):
    com = adapter.getCommunicator()
    props = com.getProperties()
    options.init(props)

    server = Server.get()
    if server.startOnLoad():
        Daemon.get().start()

    ident = com.stringToIdentity('DHCP/Server')
    adapter.add(ServerI(), ident)
    ident = com.stringToIdentity('DHCP/Daemon')
    adapter.add(DaemonI(), ident)

    adapter.addServantLocator(SubnetLocator(), "DHCP-Subnets")
    adapter.addServantLocator(HostLocator(), "DHCP-Hosts")

