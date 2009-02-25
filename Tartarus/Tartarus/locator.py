import Ice

class SimpleLocator(Ice.Locator):
    def __init__(self, adapter):
        Ice.Locator.__init__(self)
        self.__adapter = adapter
        comm = adapter.getCommunicator()
        id = comm.stringToIdentity('Locator')
        self.__prx = adapter.add(self, id)
        self.__l_prx = Ice.LocatorPrx.uncheckedCast(self.__prx)
        self.__lr_prx = Ice.LocatorRegistryPrx.uncheckedCast(self.__prx)
    def findObjectById_async(self, cb, id, current):
        prx = self.__adapter.createDirectProxy(id)
        cb.ice_response(prx)
    def findAdapterById_async(self, cb, id, current):
        prx = self.__adapter.createDirectProxy(Ice.Identity('dummy'))
        cb.ice_response(prx)
    def getRegistry(self, current):
        return None

Locator = SimpleLocator

