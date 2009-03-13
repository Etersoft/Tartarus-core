import os
import Ice
from Tartarus.iface import DHCP
from server import Server, Identity
from options import opts
from config import Config
from runner import Runner, Status
from Tartarus import auth
from Tartarus import logging

class HostI(DHCP.Host):
    def __init__(self, name):
        self.__name = name
    def __host(self):
        srv = Server.get()
        return srv.hosts()[self.__name]
    def name(self, current):
        '''string name()'''
        return self.__host().name()
    def id(self, current):
        '''HostId id()'''
        id = self.__host().identity()
        if id.type() == Identity.IDENTITY:
            return DHCP.HostId(DHCP.HostIdType.IDENTITY, id.id())
        return DHCP.HostId(DHCP.HostIdType.HARDWARE, id.hardware())
    def params(self, current):
        '''StrStrMap params()'''
        return self.__host().params().map()
    @auth.mark('admin')
    def setParam(self, key, value, current):
        '''void setParam(string key, string value)'''
        self.__host().params().set(key, value)
    @auth.mark('admin')
    def unsetParam(self, key, current):
        '''void unsetParam(string key)'''
        self.__host().params().unset(key)

class SubnetI(DHCP.Subnet):
    def __init__(self, id):
        self.__srv = Server.get()
        self.__id = id
    def __subnet(self):
        return self.__srv.subnets()[self.__id]
    def id(self, current):
        '''string id()'''
        return self.__subnet().id()
    def decl(self, current):
        '''void info(out string addr, out string mask)'''
        sbn = self.__subnet()
        return sbn.decl()
    def range(self, type, current):
        r = self.__subnet().range(type.value)
        if r is ():
            return DHCP.IpRange('', '', False)
        return DHCP.IpRange(r[0], r[1], True)
    @auth.mark('admin')
    def setRange(self, type, range, current):
        if range.hasValue:
            self.__subnet().range(type.value, (range.start, range.end))
        else:
            self.__subnet().range(type.value, ())
    def params(self, current):
        '''StrStrMap params()'''
        return self.__subnet().params().map()
    @auth.mark('admin')
    def setParam(self, key, value, current):
        '''void setParam(string key, string value)'''
        return self.__subnet().params().set(key, value)
    @auth.mark('admin')
    def unsetParam(self, key, current):
        '''void unsetParam(string key)'''
        return self.__subnet().params().unset(value)

class ServerI(DHCP.Server):
    def __init__(self):
        self.__server = Server.get()
    def subnets(self, current):
        '''SubnetSeq subnets()'''
        return [self.__mkSubnetPrx(s, current.adapter) for s in self.__server.subnets().itervalues()]
    def findSubnet(self, decl, current):
        for s in self.__server.subnets().itervalues():
            if s.decl() == decl:
                return self.__mkSubnetPrx(s, current.adapter)
    @auth.mark('admin')
    def addSubnet(self, decl, current):
        '''Subnet* addSubnet(addr, mask)'''
        s = self.__server.addSubnet(decl)
        return self.__mkSubnetPrx(s, current.adapter)
    @auth.mark('admin')
    def delSubnet(self, s, current):
        '''void delSubnet(Subnet* s)'''
        id = s.ice_getIdentity()
        self.__server.delSubnet(id.name)
    def hosts(self, current):
        '''HostSeq hosts()'''
        hosts = self.__server.hosts()
        return [self.__mkHostPrx(h, current.adapter) for h in hosts.itervalues()]
    def hostsByNames(self, names, current):
        mkprx = lambda h: self.__mkHostPrx(h, current.adapter)
        host = lambda name: self.__server.hosts().get(name, None)
        return [mkprx(host(name)) for name in names]
    @auth.mark('admin')
    def addHost(self, name, id, current):
        '''Host* addHost(string name, HostId id)'''
        if id.type == DHCP.HostIdType.IDENTITY:
            hid = Identity(id=id.value)
        else:
            hid = Identity(hardware=id.value)
        h = self.__server.addHost(name, hid)
        return self.__mkHostPrx(h, current.adapter)
    @auth.mark('admin')
    def delHosts(self, hosts):
        '''void delHosts(HostSeq hosts)'''
        pass
    def params(self, current):
        '''StrStrMap params()'''
        return self.__server.params().map()
    @auth.mark('admin')
    def setParam(self, key, value, current):
        '''void setParam(string key, string value)'''
        self.__server.params().set(key, value)
    @auth.mark('admin')
    def unsetParam(self, key, current):
        '''void unsetParam(string key)'''
        self.__server.params().unset(key, value)
    @auth.mark('admin')
    def commit(self, current):
        '''void commit()'''
        Config.get().save()
        Config.get().genDHCPCfg()
    @auth.mark('admin')
    def rollback(self, current):
        Config.get().load()
    def isConfigured(self, common):
        return Config.get().isConfigured()
    @auth.mark('admin')
    def reset(self, common):
        Config.get().reset()
    @staticmethod
    def __mkHostPrx(host, adapter):
        if host is None: return None
        comm = adapter.getCommunicator()
        id = comm.stringToIdentity('DHCP-Hosts/%s' % host.name())
        prx = adapter.createProxy(id)
        return DHCP.HostPrx.uncheckedCast(prx)
    @staticmethod
    def __mkSubnetPrx(sbn, adapter):
        if sbn is None: return None
        comm = adapter.getCommunicator()
        id = comm.stringToIdentity('DHCP-Subnets/%s' % sbn.id())
        prx = adapter.createProxy(id)
        return DHCP.SubnetPrx.uncheckedCast(prx)

class DaemonI(DHCP.Daemon):
    def __init__(self):
        self.__runner = Runner.get()
        self.__server = Server.get()
        if self.__server.startOnLoad():
            try:
                self.__runner.start()
            except RuntimeError, e:
                logging.warning(str(e))
    @auth.mark('admin')
    def start(self, current):
        self.__runner.start()
        self.__server.startOnLoad(True)
    @auth.mark('admin')
    def stop(self, current):
        self.__runner.stop()
        self.__server.startOnLoad(False)
    def running(self, current):
        return self.__runner.status() == Status.RUN

class SubnetLocator(Ice.ServantLocator):
    def locate(self, current):
        return SubnetI(current.id.name)
    def finished(self, current, servant, cookie):
        pass
    def deactivate(self, category):
        pass

class HostLocator(Ice.ServantLocator):
    def locate(self, current):
        hostname = current.id.name
        return HostI(hostname)
    def finished(self, current, servant, cookie):
        pass
    def deactivate(self, category):
        pass

def init(adapter):
    com = adapter.getCommunicator()
    dec = auth.DecoratingLocator
    adapter.addServantLocator(dec(SubnetLocator()), "DHCP-Subnets")
    adapter.addServantLocator(dec(HostLocator()), "DHCP-Hosts")

    loc = auth.SrvLocator()
    ident = com.stringToIdentity('DHCP/Server')
    loc.add_object(ServerI(), ident)
    ident = com.stringToIdentity('DHCP/Daemon')
    loc.add_object(DaemonI(), ident)
    adapter.addServantLocator(loc, "DHCP")

