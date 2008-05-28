#!/usr/bin/env python

import Tartarus, IceSSL, kadmin5

import Tartarus.iface.Kadmin5 as I # I stands for Interface

__all__ = [ "KadminI" ]

class KadminI(I.Kadmin):
    def make_kadmin(self,ctx):
        try:
            princ = IceSSL.getConnectionInfo(ctx.con).krb5Princ
            # we need to transform princ@REALM to princ/admin@REALM
            # for simplicity, we assume REALM part does not contain '@' character
            ind = princ.rfind('@')
            if ind > 0:
                if not princ[:ind].endswith("/admin"):
                    princ = princ[:ind] + "/admin" + princ[ind:]
            else:
                princ = "unknown/admin"
        except:
            princ = "Tartarus/admin"

        return kadmin5.kadmin(exc_type = I.KadminException,
                                princname=princ)

    def getPrincKeys(self, name, ctx):
        adm = self.make_kadmin(ctx)
        keys = adm.get_princ_keys(name)
        return I.PrincKeys(name,
                           [I.Key(i[0],i[1],i[2]) for i in keys])

    def createServicePrincipal(self, service, host, ctx):
        adm = self.make_kadmin(ctx)
        princ = adm.create_service_princ(service, host)
        keys = adm.get_princ_keys(princ)
        return I.PrincKeys(princ,
                           [I.Key(i[0],i[1],i[2]) for i in keys])

    def createPrincipal(self, name, password, ctx):
        adm = self.make_kadmin(ctx)
        return adm.create_princ(name, password)

    def changePrincPassword(self, name, password, ctx):
        self.make_kadmin(ctx).chpass_princ(name, password)

    def deletePrincipal(self, name, ctx):
        self.make_kadmin(ctx).delete_princ(name)

    def listPrincs(self, expr, ctx):
        return self.make_kadmin(ctx).list(expr)

    def listAllPrincs(self, ctx):
        return self.make_kadmin(ctx).list()

