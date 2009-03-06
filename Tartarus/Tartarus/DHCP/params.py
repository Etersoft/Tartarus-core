import re
from enum import Enum

Context = Enum('GLOBAL', 'SUBNET', 'RANGE', 'HOSTS', 'HOST')
Context.ALL = (
        Context.GLOBAL,
        Context.SUBNET,
        Context.RANGE,
        Context.HOSTS,
        Context.HOST)

class Option:
    def __init__(self, key, contexts=Context.ALL):
        self.__key = key
        self.__contexts = frozenset(contexts)
    def key(self):
        return self.__key
    def check(self, value):
        pass
    def repr(self, value):
        return value
    def contexts(self):
        return self.__contexts

class IpOption(Option):
    __errmsg = 'Wrong value for %s option. It must be ip-address'
    __re = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    def __init__(self, key, contexts=Context.ALL):
        Option.__init__(self, key, contexts)
    def check(self, value):
        if not self.__re.match(value): self.__fail()
        for p in (int(p) for p in value.split('.')):
            if p > 255: self.__fail()
    def __fail(self):
        raise ValueError(self.__errmsg % self.key())

class IntOption(Option):
    __errmsg = 'Value of %s option must be %d bits integer'
    __re = re.compile('^-?\d+$')
    def __init__(self, key, contexts=Context.ALL, bits=32):
        Option.__init__(self, key, contexts)
        self.__bits = bits
        self.__min = -2**(bits-1)
        self.__max = 2**(bits-1)-1
    def check(self, value):
        if not self.__re.match(value): self.__fail()
        intv = int(value)
        if intv > self.__max or intv < self.__min:
            self.__fail()
    def __fail(self):
        raise ValueError(self.__errmsg % (self.key(), self.__bits))

class UIntOption(Option):
    __errmsg = 'Value of %s option must be %d bits unsigned integer'
    __re = re.compile('^\d+$')
    def __init__(self, key, contexts=Context.ALL, bits=32):
        Option.__init__(self, key, contexts)
        self.__bits = bits
        self.__max = 2**bits-1
    def check(self, value):
        if not self.__re.match(value): self.__fail()
        intv = int(value)
        if intv > self.__max: self.__fail()
    def __fail(self):
        raise ValueError(self.__errmsg % (self.key(), self.__bits))

class TextOption(Option):
    __errmsg = 'Wrong cahacter in value of %s options'
    def __init__(self, key, context=Context.ALL, regexp=None):
        Option.__init__(self, key, contexts)
        self.__regexp = None
        if regexp:
            self.__regexp = re.compile(regexp)
    def check(self, value):
        for i in (ord(c) for c in value):
            if i < 32 or i > 126: self.__fail()
        if self.__regexp and not self.__regexp.match(value):
            self.__fail()
    def repr(self, value):
        return '"%s"' % value
    def __fail(self):
        raise ValueError(self.__errmsg % self.key())

class FlagOption(Option):
    __errmsg = 'Wrong value for %s option; valid are "on" and "off"'
    def __init__(self, key, context=Context.ALL):
        Option.__init__(self, key, contexts)
    def check(self, value):
        if value not in ('on', 'off'):
            raise ValueError(self.__errmsg % self.key())

StringOption = TextOption

class IpListOption:
    __errmsg = 'Wrong walue for %s option; valid value is list of ip-address separated by comma'
    def __init__(self, key, context):
        Option.__init__(self, key, contexts=Context.ALL)
        self.__ipopt = IpOption(key)
    def check(self, value):
        for addr in (i.strip() for i in value.split(',')):
            try:
                self.__ipopt.check(addr)
            except:
                self.__fail()
    def __fail(self):
        raise ValueError(self.__errmsg % self.key())

class _none:
    def __init__(self, key): pass
    def __call__(self, value): pass

def _regexp(key, expr):
    rexp = re.compile(expr)
    def validator(value):
        if rexp.match(value) is None:
            raise DHCPDValueError(key, value)
    return validator

def _one_of(key, *args):
    values = set(args)
    def validator(value):
        if value not in values:
            raise DHCPDValueError(key, value)
    return validator

class _ip:
    __rexp = re.compile('^\d{1,3}$')
    def __init__(self, key):
        self.__key = key
    def __call__(self, value):
        parts = value.split('.')
        if len(parts) != 4:
            raise DHCPDValueError(self.__key, value)
        for part in parts:
            if not self.__rexp.match(part):
                raise DHCPDValueError(self.__key, value)
            i = int(part)
            if i < 0 or i > 255:
                raise DHCPDValueError(self.__key, value)

class _ip_list:
    def __init__(self, key):
        self.__key = key
        self.__ip_validator = _ip(key)
    def __call__(self, value):
        try:
            for addr in value.split(','):
                self.__ip_validator(addr)
        except DHCPDValueError:
            raise DHCPDValueError(self.__key, value)

class _uint:
    __int_re = re.compile('^\d+$')
    def __init__(self, key, len):
        self.__key = key
        self.__max = 2**len-1
    def __call__(self, value):
        if not self.__int_re.match(value):
            raise DHCPDValueError(self.__key, value)
        intv = int(value)
        if intv > self.__max: raise DHCPDValueError(self.__key, value)

class _int:
    __int_re = re.compile('^-?\d+$')
    def __init__(self, key, len):
        self.__key = key
        self.__min = -2**(len-1)
        self.__max = 2**(len-1)-1
    def __call__(self, value):
        if not self.__int_re.match(value):
            raise DHCPDValueError(self.__key, value)
        intv = int(value)
        if intv > self.__max or intv < self.__min:
            raise DHCPDValueError(self.__key, value)

class _Registrator:
    def __init__(self, map):
        self.__map = map
    def __call__(self, dhcpd_optname, validator, *args):
        if dhcpd_optname.startswith('option '):
            key = dhcpd_optname[7:]
        else:
            key = dhcpd_optname
        self.__map[key] = (dhcpd_optname, validator(key, *args))

class Params:
    __opts_map = {}
    # register options
    r = _Registrator(__opts_map)
    r('always-broadcast', _one_of, 'on', 'off')
    r('always-reply-rfc1048', _one_of, 'on', 'off')
    r('authoritative', _one_of, '')
    r('not authoritative', _one_of, '')
    r('boot-unknown-clients', _one_of, 'on', 'off')
    r('default-lease-time', _regexp, '^\d+$')
    r('filename', _regexp, '^"\w+"$')
    r('fixed-address', _ip)
    r('max-lease-time', _regexp, '^\d+$')
    r('min-lease-time', _regexp, '^\d+$')
    r('min-secs', _regexp, '^\d+$')
    r('next-server', _none)
    r('one-lease-per-client', _one_of, 'on', 'off')
    r('ping-check', _one_of, 'on', 'off')
    r('ping-timeout', _regexp, '^\d+$')
    r('option all-subnets-local', _one_of, 'on', 'off')
    r('option arp-cache-timeout', _regexp, '^\d+$')
    r('option bootfile-name', _regexp,  '^"\w+"$')
    r('option boot-size', _regexp, '^\d+$')
    r('option broadcast-address', _ip)
    r('option default-ip-ttl', _regexp, '^\d+$')
    r('option default-tcp-ttl', _regexp, '^\d+$')
    r('option dhcp-lease-time', _uint, 32)
    r('option dhcp-max-message-size', _uint, 16)
    r('option dhcp-message', _regexp, '^"\w+"$')
    r('option domain-name-servers', _ip_list)
    r('option host-name', _regexp, '^"[\w\.]+"$')
    r('option interface-mtu', _uint, 16)
    r('option ip-forwarding', _one_of, 'on', 'off')
    r('option mask-supplier', _one_of, 'on', 'off')
    r('option root-path', _regexp, '^"\w+"$')
    r('option routers', _ip_list)
    r('option tftp-server-name', _regexp, '^"[\w\.]+"$')
    r('option time-offset', _int, 32)
    r('option time-servers', _ip_list)
    del r
    # end register options
    def __init__(self):
        self.__map = {}
    def set(self, key, value):
        if key not in self.__opts_map:
            raise DHCPDKeyError(key)
        # check value is valid
        _, validator = self.__opts_map[key]
        validator(value)
        self.__map[key] = value
    def unset(self, key):
        if key in self.__map:
            del self.__map[key]
    def map(self):
        return self.__map
    def iter(self):
        for key, value in self.__map.iteritems():
            dhcpd_optname, _ = self.__opts_map[key]
            yield dhcpd_optname, value

class DHCPDValueError(RuntimeError):
    def __init__(self, key, value):
        RuntimeError.__init__(self, 'Wrong value "%s" for %s option' % (key, value))
        self.key = key
        self.value = value

class DHCPDKeyError(RuntimeError):
    def __init__(self, key):
        RuntimeError.__init__(self, 'Unknown option %s' % key)
        self.key = key

