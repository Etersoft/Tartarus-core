from socket import inet_aton, inet_ntoa
from struct import pack, unpack
from itertools import izip, islice

class IpAddr(object):
    __slots__ = 'int', 'str'
    def __init__(self, addr):
        if isinstance(addr, int) or isinstance(addr, long):
            try: self.str = inet_ntoa(pack('>I', addr))
            except: raise ValueError('illegal IP address integer')
            self.int = addr
        elif isinstance(addr, IpAddr):
            self.int = addr.int
            self.str = addr.str
        else:
            try: self.int = unpack('>I', inet_aton(addr))[0]
            except: raise ValueError('illegal IP address string "%s"' % addr)
            self.str = addr
    def __repr__(self):
        return 'IpAddr(%s)' % self.str

class IpRange(object):
    def __init__(self, start, end):
        self.start = IpAddr(start)
        self.end = IpAddr(end)
        if self.start.int > self.end.int:
            raise ValueError('start address in IpRange should be less then end address')
    @staticmethod
    def sort(list):
        list.sort(key=lambda r: r.start.int)
    @staticmethod
    def intersect(list):
        for r1, r2 in izip(list, islice(list, 1, None)):
            if r1.end.int >= r2.start.int:
                return True
        return False
    def __contains__(self, val):
        if isinstance(val, IpRange):
            return (val.start.int >= self.start.int
                    and val.end.int <= self.end.int)
        if not isinstance(val, IpAddr):
            addr = IpAddr(val)
        else:
            addr = val
        return addr.int >= self.start.int and addr.int <= self.end.int
    def __repr__(self):
        return 'IpRange(%s, %s)' % (self.start.str, self.end.str)

class IpMask(object):
    def __init__(self, mask):
        if mask < 0 or mask > 32: raise ValueError('illegal value for IP mask')
        self.int = mask
        bits = 0
        for i in xrange(32-mask, 32):
            bits |= (1 << i)
        self.str = inet_ntoa(pack('>I', bits))
    def prefix(self, addr):
        if not isinstance(addr, IpAddr):
            addr = IpAddr(addr)
        zb = 32 - self.int
        return IpAddr((addr.int >> zb) << zb)
    def maxAddr(self, addr):
        min_addr = self.prefix(addr).int
        add = 0
        for i in xrange(0, 32-self.int):
            add |= (1 << i)
        return IpAddr(min_addr + add)
    def __repr__(self):
        return 'IpMask(%d)' % self.int

class IpSubnet(IpRange):
    def __init__(self, subnet):
        parts = subnet.split('/')
        if len(parts) != 2: raise ValueError('illegal IP subnet string')
        addr, mask = parts
        try: mask = int(mask)
        except: raise ValueError('illegal value for IP mask')
        self.mask = IpMask(mask)
        self.prefix = self.mask.prefix(addr)
        self.cidr = '%s/%d' % (self.prefix.str, self.mask.int)
        IpRange.__init__(self, self.prefix, self.mask.maxAddr(self.prefix))
    def __repr__(self):
        return 'IpSubnet(%s)' % self.cidr

