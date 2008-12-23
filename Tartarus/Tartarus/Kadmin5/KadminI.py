
import Tartarus, kadmin5
import Tartarus.iface.Kerberos as I # I stands for Interface
from Tartarus import auth

import kdb

__all__ = [ "KadminI" ]

class KadminI(I.Kadmin):
    def __init__(self, kdbi):
        self._kdb = kdbi


    @auth.mark('admin')
    @kdb.wrap
    def getPrincKeys(self, adm, name, current):
        keys = adm.get_princ_keys(name)
        return I.PrincKeys(name, [I.Key(*i) for i in keys])

    @auth.mark('admin')
    @kdb.wrap
    def createServicePrincipal(self, adm, service, host, current):
        princ = adm.create_service_princ(service, host)
        keys = adm.get_princ_keys(princ)
        return I.PrincKeys(princ, [I.Key(*i) for i in keys])

    @auth.mark('admin')
    @kdb.wrap
    def randomizeServicePrincKeys(self, adm, service, host, current):
        princ = "%s/%s" % (service, host)
        adm.randkey_princ(princ)
        keys = adm.get_princ_keys(princ)
        return I.PrincKeys("%s@%s" % (princ, adm.get_realm()),
                           [I.Key(*i) for i in keys])


    @auth.mark('admin')
    @kdb.wrap
    def createPrincipal(self, adm, name, password, current):
        return adm.create_princ(name, password)

    @auth.mark('admin')
    @kdb.wrap
    def changePrincPassword(self, adm, name, password, current):
        adm.chpass_princ(name, password)

    @auth.mark('admin')
    @kdb.wrap
    def deletePrincipal(self, adm, name, current):
        adm.delete_princ(name)

    @auth.mark('read')
    @kdb.wrap
    def listPrincs(self, adm, expr, current):
        return adm.list(expr)

    @auth.mark('read')
    @kdb.wrap
    def listAllPrincs(self, adm, current):
        return adm.list()

    _disabling_attrs = kadmin5.attributes.DISALLOW_ALL_TIX

    @auth.mark('read')
    @kdb.wrap
    def isPrincEnabled(self, adm, name, current):
        attrs = adm.get_princ_attributes(name)
        return (attrs & self._disabling_attrs) == 0

    @auth.mark('admin')
    @kdb.wrap
    def setPrincEnabled(self, adm, name, enable, current):
        attrs = adm.get_princ_attributes(name)
        if enable:
            attrs &= ~self._disabling_attrs
        else:
            attrs |= self._disabling_attrs
        adm.set_princ_attributes(name, attrs)

