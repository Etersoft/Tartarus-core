from params import Params
from uuid import uuid4 as uuid
import re
import os
from Cheetah.Template import Template

from Tartarus.system.ipaddr import IpSubnet, IpRange

STATIC = 1;
KNOWN = 2;
UNKNOWN = 4;

class Server:
    __instance = None
    @staticmethod
    def get():
        if Server.__instance is None:
            Server.__instance = Server()
        return Server.__instance
    def __init__(self):
        self.__start_on_load = False
        self.reset()
    def reset(self):
        self.__params = Params()
        self.__subnets = {}
        self.__hosts = {}
    def params(self):
        return self.__params
    def subnets(self):
        return self.__subnets.itervalues()
    def getSubnet(self, id):
        return self.__subnets[id]
    def findSubnet(self, addr):
        for s in self.subnets():
            if addr in s: return s
    def findRange(self, addr):
        s = self.findSubnet(addr)
        if s: return s.findRange(addr)
    def addSubnet(self, decl):
        sn = _Subnet(str(uuid()), decl)
        self.__subnets[sn.id()] = sn
        return sn
    def delSubnet(self, id):
        del self.__subnets[id]
    def restoreSubnet(self, id, decl):
        sn = _Subnet(id, decl)
        self.__subnets[id] = sn
        return sn
    def hosts(self):
        return self.__hosts.itervalues()
    def getHost(self, name):
        return self.__hosts[name]
    def addHost(self, name, id):
        h = _Host(name, id)
        self.__hosts[name] = h
        return h
    def delHost(self, name):
        del self.__hosts[name]
    def startOnLoad(self, value=None):
        if value is None:
            return self.__start_on_load
        self.__start_on_load = value
    def genConfig(self, file):
        tpl_path = os.path.join(os.path.dirname(__file__), 'dhcpd_conf.tmpl')
        dhcpd_conf = Template.compile(file=open(tpl_path))
        cfg_gen = dhcpd_conf()
        cfg_gen.server = self
        file.write(str(cfg_gen))

class _Subnet(IpSubnet):
    re = re.compile('^\d{1,3}$')
    def __init__(self, id, decl):
        IpSubnet.__init__(self, decl)
        self.__id = id
        self.__params = Params()
        self.__ranges = {}
    def id(self):
        return self.__id
    def params(self):
        return self.__params
    def ranges(self):
        return self.__ranges.itervalues()
    def getRange(self, id):
        return self.__ranges[id]
    def findRange(self, addr):
        for r in self.ranges():
            if addr in r: return r
    def addRange(self, start, end, caps):
        r = _Range(str(uuid()), start, end, caps, self)
        if r not in self: raise ValueError('Range not in subnet')
        ranges = self.__ranges.values()
        ranges.append(r)
        IpRange.sort(ranges)
        if IpRange.intersect(ranges): raise ValueError('Intersection in ranges')
        self.__ranges[r.id()] = r
        return r
    def delRange(self, id):
        del self.__ranges[id]
    def restoreRange(self, id, start, end, caps):
        r = _Range(id, start, end, caps, self)
        self.__ranges[id] = r
        return r

class _Range(IpRange):
    def __init__(self, id, start, end, caps, subnet):
        IpRange.__init__(self, start, end)
        self.__id = id
        self.__start = start
        self.__end = end
        self.__caps = caps
        self.__subnet = subnet
        self.__params = Params()
    def id(self):
        return self.__id
    def caps(self, caps=None):
        if caps is not None:
            self.__caps = caps
        else:
            return self.__caps
    def staticCap(self):
        return bool(self.__caps & STATIC)
    def knownCap(self):
        return bool(self.__caps & KNOWN)
    def unknownCap(self):
        return bool(self.__caps & UNKNOWN)
    def subnet(self):
        return self.__subnet
    def params(self):
        return self.__params

class Identity:
    IDENTITY, HARDWARE = range(2)
    def __init__(self, id=None, hardware=None):
        if id is None and hardware is not None:
            self.__id = None
            self.__hardware = hardware
        elif id is not None and hardware is None:
            self.__id = id
            self.__hardware = None
        else:
            raise TypeError('Wrong parameters while construct host identity')
    def type(self):
        if self.__id:
            return self.IDENTITY
        else:
            return self.HARDWARE
    def id(self):
        return self.__id
    def hardware(self):
        return self.__hardware
    def __str__(self):
        if self.__id:
            return 'option dhcp-client-identifier %s;' % self.__id
        return 'hardware %s;' % self.__hardware

class _Host:
    def __init__(self, name, id):
        self.__name = name
        self.__id = id
        self.__params = Params()
    def name(self):
        return self.__name
    def identity(self):
        return self.__id
    def idLine(self):
        return str(self.__id)
    def params(self):
        return self.__params

STATIC, TRUST, UNTRUST = range(3)

_tmpl = '''

'''

