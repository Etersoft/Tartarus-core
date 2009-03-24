import re
from menum import Enum

Context = Enum('GLOBAL', 'SUBNET', 'RANGE', 'HOSTS', 'HOST')
Context.ALL = (
        Context.GLOBAL,
        Context.SUBNET,
        Context.RANGE,
        Context.HOSTS,
        Context.HOST)

class Option(object):
    __all = {}
    def __init__(self, key, dhcp_key=None, contexts=Context.ALL):
        self.__key = key
        self.__dhcp_key = dhcp_key or key
        self.__contexts = frozenset(contexts)
        self.__all[key] = self
    def key(self):
        return self.__key
    def dhcpKey(self):
        return self.__dhcp_key
    def check(self, value):
        pass
    def repr(self, value):
        return value
    def contexts(self):
        return self.__contexts
    @staticmethod
    def opt(key):
        return Option.__all.get(key, None)

opt = Option.opt

class IpOption(Option):
    __errmsg = 'Wrong value for %s option. It must be ip-address'
    __re = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    def __init__(self, key, dhcp_key=None, contexts=Context.ALL):
        Option.__init__(self, key, dhcp_key, contexts)
    def check(self, value):
        if not self.__re.match(value): self.__fail()
        for p in (int(p) for p in value.split('.')):
            if p > 255: self.__fail()
    def __fail(self):
        raise ValidationError(self.__errmsg % self.key())

class IntOption(Option):
    __errmsg = 'Value of %s option must be %d bits integer'
    __re = re.compile('^-?\d+$')
    def __init__(self, key, dhcp_key=None, contexts=Context.ALL, bits=32):
        Option.__init__(self, key, dhcp_key, contexts)
        self.__bits = bits
        self.__min = -2**(bits-1)
        self.__max = 2**(bits-1)-1
    def check(self, value):
        if not self.__re.match(value): self.__fail()
        intv = int(value)
        if intv > self.__max or intv < self.__min:
            self.__fail()
    def __fail(self):
        raise ValidationError(self.__errmsg % (self.key(), self.__bits))

class UIntOption(Option):
    __errmsg = 'Value of %s option must be %d bits unsigned integer'
    __re = re.compile('^\d+$')
    def __init__(self, key, dhcp_key=None, contexts=Context.ALL, bits=32):
        Option.__init__(self, key, dhcp_key, contexts)
        self.__bits = bits
        self.__max = 2**bits-1
    def check(self, value):
        if not self.__re.match(value): self.__fail()
        intv = int(value)
        if intv > self.__max: self.__fail()
    def __fail(self):
        raise ValidationError(self.__errmsg % (self.key(), self.__bits))

class TextOption(Option):
    __errmsg = 'Wrong cahacter in value of %s options'
    def __init__(self, key, dhcp_key=None, contexts=Context.ALL, regexp=None):
        Option.__init__(self, key, dhcp_key, contexts)
        self.__regexp = None
        if regexp:
            self.__regexp = re.compile(regexp)
    def check(self, value):
        for i in (ord(c) for c in value):
            if i < 32 or i > 126 or i in (34,): self.__fail()
        if self.__regexp and not self.__regexp.match(value):
            self.__fail()
    def repr(self, value):
        return '"%s"' % value
    def __fail(self):
        raise ValidationError(self.__errmsg % self.key())

class FlagOption(Option):
    __errmsg = 'Wrong value for %s option; valid are "on" and "off"'
    def __init__(self, key, dhcp_key=None, contexts=Context.ALL):
        Option.__init__(self, key, dhcp_key, contexts)
    def check(self, value):
        if value not in ('on', 'off'):
            raise ValidationError(self.__errmsg % self.key())

StringOption = TextOption

class IpListOption(Option):
    __errmsg = 'Wrong walue for %s option; valid value is list of ip-address separated by comma'
    def __init__(self, key, dhcp_key=None, contexts=Context.ALL):
        Option.__init__(self, key, dhcp_key, contexts)
        self.__ipopt = IpOption(key)
    def check(self, value):
        for addr in (i.strip() for i in value.split(',')):
            try:
                self.__ipopt.check(addr)
            except:
                self.__fail()
    def __fail(self):
        raise ValidationError(self.__errmsg % self.key())

FlagOption('always-broadcast')
FlagOption('always-reply-rfc1048')
FlagOption('boot-unknown-clients')
UIntOption('default-lease-time')
StringOption('filename')
IpListOption('fixed-address')
UIntOption('max-lease-time')
UIntOption('min-lease-time')
UIntOption('min-secs')
Option('next-server')
FlagOption('one-lease-per-client')
FlagOption('ping-check')
UIntOption('ping-timeout')

FlagOption('all-subnets-local', 'option all-subnets-local')
UIntOption('arp-cache-timeout', 'option arp-cache-timeout')
TextOption('bootfile-name', 'option bootfile-name')
UIntOption('boot-size', 'option boot-size', bits=16)
IpOption('broadcast-address', 'option broadcast-address')
UIntOption('default-ip-ttl', 'option default-ip-ttl', bits=8)
UIntOption('default-tcp-ttl', 'option default-tcp-ttl', bits=8)
UIntOption('dhcp-lease-time', 'option dhcp-lease-time')
UIntOption('dhcp-max-message-size', 'option dhcp-max-message-size', bits=16)
TextOption('dhcp-message', 'option dhcp-message')
IpListOption('domain-name-servers', 'option domain-name-servers')
StringOption('host-name', 'option host-name')
UIntOption('interface-mtu', 'option interface-mtu', bits=16)
FlagOption('ip-forwarding', 'option ip-forwarding')
FlagOption('mask-supplier', 'option mask-supplier')
TextOption('root-path', 'option root-path')
IpListOption('routers', 'option routers')
TextOption('tftp-server-name', 'option tftp-server-name')
IntOption('time-offset', 'option time-offset')
IpListOption('time-servers', 'option time-servers')

class Params:
    def __init__(self):
        self.__map = {}
    def set(self, key, value):
        o = opt(key)
        if not o: raise KeyError(key)
        try:
            o.check(value)
        except ValidationError, e:
            raise ValueError(key, value, str(e))
        self.__map[key] = value
    def unset(self, key):
        if key in self.__map:
            del self.__map[key]
    def map(self):
        return self.__map
    def iter(self):
        for key, value in self.__map.iteritems():
            o = opt(key)
            yield o.dhcpKey(), o.repr(value)

class ValueError(RuntimeError):
    def __init__(self, key, value, what):
        RuntimeError.__init__(self, what)
        self.key = key
        self.value = value

class KeyError(RuntimeError):
    def __init__(self, key):
        RuntimeError.__init__(self, 'Invalid option key: "%s"' % key)
        self.key = key

class ValidationError(RuntimeError): pass

