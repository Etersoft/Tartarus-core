
import Tartarus
from Tartarus import logging
import Tartarus.iface.DNS as I


class ServerI(I.Server):
    def getDomains(current):
        return I.DomainSeq()

    def getDomain(name, current):
        return None

    def createDomain(name, current):
        return None

    def deleteDomain(name, current):
        pass

    def deleteDomainByRef(proxy, current):
        pass

    def getOptions(current):
        return I.ServerOptionSeq()

    def setOptions(opts, current):
        pass

    def setOption(opt, current):
        pass


