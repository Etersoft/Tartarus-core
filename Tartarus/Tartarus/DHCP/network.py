import os
from functools import wraps
import Ice
from Tartarus.iface import DHCP
from server import Server, Identity
from options import opts
from config import Config
from runner import Runner, Status
from params import KeyError, ValueError
from Tartarus import auth
from Tartarus import logging

def exceptm(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except KeyError, e:
            raise DHCP.KeyError(str(e), e.key)
        except ValueError, e:
            raise DHCP.ValueError(str(e), e.key, e.value)
    return wrapper

class ScopeI(DHCP.Scope):
    def options(self, current):
        return self.getObj().params().map()
    @auth.mark('admin')
    @exceptm
    def setOption(self, key, value, current):
        self.getObj().params().set(key, value)
        Config.get().save()
    @auth.mark('admin')
    def unsetOption(self, key, current):
        self.getObj().params().unset(key)
        Config.get().save()

class HostI(ScopeI, DHCP.Host):
    def __init__(self, name):
        self.__name = name
    def __host(self):
        srv = Server.get()
        return srv.getHost(self.__name)
    getObj = __host
    def name(self, current):
        '''string name()'''
        return self.__host().name()
    def id(self, current):
        '''HostId id()'''
        id = self.__host().identity()
        if id.type() == Identity.IDENTITY:
            return DHCP.HostId(DHCP.HostIdType.IDENTITY, id.id())
        return DHCP.HostId(DHCP.HostIdType.HARDWARE, id.hardware())

class SubnetI(DHCP.Subnet):
    def __init__(self, id):
        self.__srv = Server.get()
        self.__id = id
    def __subnet(self):
        return self.__srv.getSubnet(self.__id)
    getObj = __subnet
    def id(self, current):
        '''string id()'''
        return self.__subnet().id()
    def cidr(self, current):
        sbn = self.__subnet()
        return sbn.cidr
    def ranges(self, current):
        return [self.mkRangePrx(r, current.adapter) for r in self.__subnet().ranges()]
    def getRange(self, id, current):
        return self.mkRangePrx(self.__subnet().getRange(id), current.adapter)
    def findRange(self, addr, current):
        return self.mkRangePrx(self.__subnet().findRange(addr), current.adapter)
    @auth.mark('admin')
    def addRange(self, start, end, caps, current):
        r = self.__subnet().addRange(start, end, caps)
        Config.get().save()
        return self.mkRangePrx(r, current.adapter)
    @auth.mark('admin')
    def delRange(self, id, current):
        self.__subnet().delRange(id)
        Config.get().save()
    @staticmethod
    def mkRangePrx(range, adapter):
        if range is None: return None
        comm = adapter.getCommunicator()
        id = comm.stringToIdentity('DHCP-Ranges/%s.%s' % (range.subnet().id(), range.id()))
        prx = adapter.createProxy(id)
        return DHCP.RangePrx.uncheckedCast(prx)

class RangeI(ScopeI, DHCP.Range):
    def __init__(self, name):
        srv = Server.get()
        sid, rid = name.split('.')
        self.__range = srv.getSubnet(sid).getRange(rid)
    def getObj(self):
        return self.__range
    def id(self, current):
        return self.__range.id()
    def caps(self, current):
        return self.__range.caps()
    @auth.mark('admin')
    def setCaps(self, caps, current):
        self.__range.caps(caps)
        Config.get().save()
    def addrs(self, current):
        return self.__range.start.str, self.__range.end.str

class ServerI(ScopeI, DHCP.Server):
    def __init__(self):
        self.__server = Server.get()
    def getObj(self):
        return self.__server
    def subnets(self, current):
        '''SubnetSeq subnets()'''
        return [self.__mkSubnetPrx(s, current.adapter) for s in self.__server.subnets()]
    def findSubnet(self, addr, current):
        s = self.__server.findSubnet(addr)
        if s: return self.__mkSubnetPrx(s, current.adapter)
    @auth.mark('admin')
    def addSubnet(self, decl, current):
        '''Subnet* addSubnet(addr, mask)'''
        s = self.__server.addSubnet(decl)
        Config.get().save()
        return self.__mkSubnetPrx(s, current.adapter)
    @auth.mark('admin')
    def delSubnet(self, id, current):
        '''void delSubnet(Subnet* s)'''
        self.__server.delSubnet(id)
        Config.get().save()
    def hosts(self, current):
        '''HostSeq hosts()'''
        hosts = self.__server.hosts()
        return [self.__mkHostPrx(h, current.adapter) for h in hosts]
    def getHost(self, name, current):
        host = self.__server.getHost(name)
        return self.__mkHostPrx(host, current.adapter)
    @auth.mark('admin')
    def addHost(self, name, id, current):
        '''Host* addHost(string name, HostId id)'''
        if id.type == DHCP.HostIdType.IDENTITY:
            hid = Identity(id=id.value)
        else:
            hid = Identity(hardware=id.value)
        h = self.__server.addHost(name, hid)
        Config.get().save()
        return self.__mkHostPrx(h, current.adapter)
    @auth.mark('admin')
    def delHost(self, name, current):
        '''void delHosts(HostSeq hosts)'''
        self.__server.delHost(name)
        Config.get().save()
    def findRange(self, addr, current):
        r = self.__server.findRange(addr)
        if r: return SubnetI.mkRangePrx(r, current.adapter)
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
        Config.get().genDHCPCfg()
        self.__runner.start()
        self.__server.startOnLoad(True)
        Config.get().save()
    @auth.mark('admin')
    def stop(self, current):
        self.__runner.stop()
        self.__server.startOnLoad(False)
        Config.get().save()
    def running(self, current):
        return self.__runner.status() == Status.RUN

class SubnetLocator(Ice.ServantLocator):
    def locate(self, current):
        return SubnetI(current.id.name)
    def finished(self, current, servant, cookie):
        pass
    def deactivate(self, category):
        pass

class RangeLocator(Ice.ServantLocator):
    def locate(self, current):
        r = RangeI(current.id.name)
        return r
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
    adapter.addServantLocator(dec(RangeLocator()), "DHCP-Ranges")
    adapter.addServantLocator(dec(HostLocator()), "DHCP-Hosts")

    loc = auth.SrvLocator()
    ident = com.stringToIdentity('DHCP/Server')
    loc.add_object(ServerI(), ident)
    ident = com.stringToIdentity('DHCP/Daemon')
    loc.add_object(DaemonI(), ident)
    adapter.addServantLocator(loc, "DHCP")

