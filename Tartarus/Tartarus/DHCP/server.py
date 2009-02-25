from params import Params
from uuid import uuid4 as uuid
import re
import os
from socket import inet_ntoa, inet_aton
from struct import pack
#from dhcpd_conf import dhcpd_conf
from Cheetah.Template import Template

class IpMask:
    @staticmethod
    def i2s(mask):
        bits = 0
        for i in xrange(32-mask,32):
            bits |= (1 << i)
        return inet_ntoa(pack('>I', bits))
    @staticmethod
    def s2i(mask):
        mask = inet_aton(mask)
        i = unpack('I', mask)[0]
        return int(math.log(i+1,2)+0.1)

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
        return self.__subnets
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
        return self.__hosts
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

class _Subnet:
    re = re.compile('^\d{1,3}$')
    def __init__(self, id, decl):
        addr, mask = decl.split('/')
        mask = IpMask.i2s(int(mask))
        self.__testAddr(addr)
        self.__id = id
        self.__decl = decl
        self.__addr = addr
        self.__mask = mask
        self.__params = Params()
        self.__ranges = [()]*3
    def id(self):
        return self.__id
    def decl(self):
        return self.__decl
    def addr(self):
        return self.__addr
    def mask(self):
        return self.__mask
    def params(self):
        return self.__params
    def range(self, rtype, value=None):
        if value is None:
            return self.__ranges[rtype]
        self.__ranges[rtype] = value
    @staticmethod
    def __testAddr(addr):
        parts = addr.split('.')
        if len(parts) != 4:
            raise RuntimeError('Wrong subnet address: %s' % addr)
        for part in parts:
            if not _Subnet.re.match(part) or int(part) > 255:
                raise RuntimeError('Wrong subnet address: %s' % addr)

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

