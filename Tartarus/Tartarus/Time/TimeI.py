
import Tartarus
import Tartarus.iface.Time as I # I stands for Interface
from Tartarus import auth

import time

__all__ = [ "TimeI" ]

class TimeI(I.Server):
    def __init__(self):
        pass

    def _tm(self, t):
        return I.tm(t.tm_sec,
                    t.tm_min,
                    t.tm_hour,
                    t.tm_mday,
                    t.tm_mon,
                    t.tm_year,
                    t.tm_wday,
                    t.tm_yday)

    @auth.mark('read')
    def getGMTime(self, current):
        return self._tm(time.gmtime())

    @auth.mark('read')
    def getLocalTime(self, current):
        return self._tm(time.localtime())

    @auth.mark('read')
    def getTime(self, current):
        return int(time.time())
