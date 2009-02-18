import os
from subprocess import Popen, PIPE
import Ice
import signal
from Tartarus.iface import DHCP
from internal import Server, Identity
import storage

class Saver:
    __instance = None
    @staticmethod
    def get():
        if Saver.__instance is None:
            raise RuntimeError('Saver instance is not initialized')
        return Saver.__instance
    def __init__(self, cfg_fname, dhcp_cfg_fname):
        Saver.__instance = self
        self.__server = Server.get()
        self.__cfg_fname = cfg_fname
        self.__cfg_fname_new = cfg_fname + '.new'
        self.__dhcp_cfg_fname = dhcp_cfg_fname
        self.__dhcp_cfg_fname_new = dhcp_cfg_fname + '.new'
    def save(self):
        storage.save(self.__server, open(self.__cfg_fname_new, 'w+'))
        os.rename(self.__cfg_fname_new, self.__cfg_fname)
    def load(self):
        self.__server.reset()
        if os.path.exists(self.__cfg_fname):
            storage.load(self.__server, open(self.__cfg_fname))
    def cfgPath(self):
        return self.__dhcp_cfg_fname
    def genConfig(self):
        self.__server.genConfig(open(self.__dhcp_cfg_fname_new, 'w+'))
        os.rename(self.__dhcp_cfg_fname_new, self.__dhcp_cfg_fname)

class Daemon:
    RUN, STOP = range(2)
    __instance = None
    @staticmethod
    def get():
        if Daemon.__instance is None:
            Daemon.__instance = Daemon()
        return Daemon.__instance
    def __init__(self):
        self.__program = 'dhcpd'
        self.__pid = None
        self.__args = [
                'dhcpd',
                '-f',
                '-q',
                '-cf', Saver.get().cfgPath()
                ]
    def start(self):
        if self.status() == self.RUN:
            return
        self.test_cfg()
        self.__pid = os.spawnvp(os.P_NOWAIT, self.__program, self.__args)
    def stop(self):
        if self.status() == self.STOP:
            return
        os.kill(self.__pid, signal.SIGTERM)
        self.__waitpid()
    def status(self):
        if self.__pid is None:
            return self.STOP
        statfile = '/proc/%d/stat' % self.__pid
        if os.path.exists(statfile):
            statcontent = open(statfile).read()
            stat = statcontent.split()
            if stat[1] == '(dhcpd)' and stat[2] != 'Z':
                return self.RUN
            if stat[1] == '(dhcpd)' and stat[2] == 'Z':
                self.__waitpid()
        return self.STOP
    def test_cfg(self):
        sp = Popen(['dhcpd', '-t', '-cf', Saver.get().cfgPath()], stderr=PIPE)
        _, errors = sp.communicate()
        if sp.returncode != 0:
            raise RuntimeError(errors)
    def __waitpid(self):
        os.waitpid(self.__pid, 0)
        self.__pid = None

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
    def setParam(self, key, value, current):
        '''void setParam(string key, string value)'''
        self.__host().params().set(key, value)
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
        print type, type.value
        r = self.__subnet().range(type.value)
        if r is ():
            return DHCP.IpRange('', '', False)
        return DHCP.IpRange(r[0], r[1], True)
    def setRange(self, type, range, current):
        if range.hasValue:
            self.__subnet().range(type.value, (range.start, range.end))
        else:
            self.__subnet().range(type.value, ())
    def params(self, current):
        '''StrStrMap params()'''
        return self.__subnet().params().map()
    def setParam(self, key, value, current):
        '''void setParam(string key, string value)'''
        return self.__subnet().params().set(key, value)
    def unsetParam(self, key, current):
        '''void unsetParam(string key)'''
        return self.__subnet().params().unset(value)

class ServerI(DHCP.Server):
    def __init__(self):
        self.__server = Server.get()
    def apply(self):
        pass
    def reset(self):
        pass
    def subnets(self, current):
        '''SubnetSeq subnets()'''
        return [self.__mkSubnetPrx(s, current.adapter) for s in self.__server.subnets().itervalues()]
    def findSubnet(self, decl, current):
        for s in self.__server.subnets().itervalues():
            if s.decl() == decl:
                return self.__mkSubnetPrx(s, current.adapter)
    def addSubnet(self, decl, current):
        '''Subnet* addSubnet(addr, mask)'''
        s = self.__server.addSubnet(decl)
        return self.__mkSubnetPrx(s, current.adapter)
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
    def addHost(self, name, id, current):
        '''Host* addHost(string name, HostId id)'''
        if id.type == DHCP.HostIdType.IDENTITY:
            hid = Identity(id=id.value)
        else:
            hid = Identity(hardware=id.value)
        h = self.__server.addHost(name, hid)
        return self.__mkHostPrx(h, current.adapter)
    def delHosts(self, hosts):
        '''void delHosts(HostSeq hosts)'''
        pass
    def params(self, current):
        '''StrStrMap params()'''
        return self.__server.params().map()
    def setParam(self, key, value, current):
        '''void setParam(string key, string value)'''
        self.__server.params().set(key, value)
    def unsetParam(self, key, current):
        '''void unsetParam(string key)'''
        self.__server.params().unset(key, value)
    def commit(self, current):
        '''void commit()'''
        Saver.get().save()
        Saver.get().genConfig()
    def reset(self, current):
        Saver.get().load()
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
        self.__daemon = Daemon.get()
        self.__server = Server.get()
    def start(self, current):
        self.__daemon.start()
        self.__server.startOnLoad(True)
    def stop(self, current):
        self.__daemon.stop()
        self.__server.startOnLoad(False)
    def running(self, current):
        return self.__daemon.status() == Daemon.RUN

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

