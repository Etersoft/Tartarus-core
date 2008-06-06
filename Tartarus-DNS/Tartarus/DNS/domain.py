
import Tartarus, Ice
from Tartarus import logging
import Tartarus.iface.DNS as I

from Tartarus.DNS.db import get_connection

class Locator(Ice.ServantLocator):
    def __init__(self):
        self.obj = DomainI();
    def locate(self, current, cookie):
        return self.obj
    def finished(self, current, obj, cookie):
        pass
    def deactivate(self, category):
        pass


class DomainI(I.Domain):
    def addRecord(r, current):
        pass

    def addRecords(rs, current):
        pass

    def clearAll(current):
        pass

    def dropRecord(name, type, current):
        pass

    def getRecords(offset, limit, current):
        pass

    def countRecords(current):
        pass

    def findRecords(phrase, limit, current):
        pass

    def getSOA(current):
        pass

    def setSOA(soar, current):
        pass

