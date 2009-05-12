
import Tartarus
import Tartarus.iface.core as C

class service(C.Service):
    def __init__(self):
        pass

    def getName(self, current):
        return 'Time'

    def isConfigured(self, current):
        return True

    def configure(self, params, current):
        pass
