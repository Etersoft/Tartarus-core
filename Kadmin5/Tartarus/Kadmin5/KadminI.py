#!/usr/bin/env python

import Tartarus, IceSSL, kadmin5

import Tartarus.iface.Kadmin5 as I # I stands for Interface

__all__ = [ "KadminI" ]

def run_command(args, msg):
    try:
        import subprocess
        p = subprocess.Popen(args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        res = p.wait()
        s = p.communicate()[1]
        if res != 0:
            raise I.KadminException(res, msg, s)
    except OSError, e:
        raise I.KadminException(e.errno, msg, e.strerror)


class KadminI(I.Kadmin):
    def __init__(self, enable_deploy=False):
        self.enable_deploy = enable_deploy
        # test configuration:
        if not enable_deploy:
            self.make_kadmin(None)

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
        return I.PrincKeys(name, [I.Key(*i) for i in keys])

    def createServicePrincipal(self, service, host, ctx):
        adm = self.make_kadmin(ctx)
        princ = adm.create_service_princ(service, host)
        keys = adm.get_princ_keys(princ)
        return I.PrincKeys(princ, [I.Key(*i) for i in keys])

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

    _disabling_attrs = kadmin5.attributes.DISALLOW_ALL_TIX

    def isPrincEnabled(self, name, ctx):
        attrs = self.make_kadmin(ctx).get_princ_attributes(name)
        return (attrs & self._disabling_attrs) == 0

    def setPrincEnabled(self, name, enable, ctx):
        adm = self.make_kadmin(ctx)
        attrs = adm.get_princ_attributes(name)
        if enable:
            attrs &= ~self._disabling_attrs
        else:
            attrs |= self._disabling_attrs
        adm.set_princ_attributes(name, attrs)

    def reGenerateDatabase(self, password, ctx):
        if not self.enable_deploy:
            raise I.KadminException(-1,
                    "Failed to create new database",
                    "This function was disabled")
        run_command(["kdb5_util", "destroy", "-f"],
                "Failed to destroy existing database")

        run_command(["kdb5_util", "create", "-s", "-P", password],
                "Failed to create database")


