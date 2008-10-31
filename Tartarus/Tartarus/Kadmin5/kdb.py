
from __future__ import with_statement

import kadmin5, Tartarus, threading, functools, subprocess, IceSSL

import Tartarus.iface.Kadmin5 as I
import Tartarus.iface.core as ICore


def _run_command(args, msg):
    try:
        p = subprocess.Popen(args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        res = p.wait()
        s = p.communicate()[1]
        if res != 0:
            raise ICore.RuntimeError(s)
    except OSError, e:
        raise ICore.RuntimeError(msg + ': ' + e.strerror)


class Kdb(object):
    def __init__(self, enable_deploy, realm=None):
        self.lock = threading.Lock()
        self.realm = realm
        self.enable_deploy = enable_deploy

    def kadmin(self, ctx):
        try:
            princ = IceSSL.getConnectionInfo(ctx.con).krb5Princ
            # we need to transform princ@REALM to princ/admin@REALM
            # for simplicity, we assume REALM part does not contain
            # '@' character
            ind = princ.rfind('@')
            if ind > 0:
                if not princ[:ind].endswith("/admin"):
                    princ = princ[:ind] + "/admin" + princ[ind:]
            else:
                princ = "unknown/admin"
        except Exception:
            princ = "Tartarus/admin"

        result = kadmin5.kadmin(exc_type = I.KadminException,
                                princname=princ, realm=self.realm)
        if not self.realm:
            self.realm = result.get_realm()

        return result

    def remove(self):
        if not self.enable_deploy:
            raise I.KadminException(-1,
                    "Failed to create new database",
                    "This function was disabled")
        command = ["kdb5_util", "destroy", "-f"]
        if self.realm:
            command += ["-r", self.realm]
        _run_command(command, "Failed to destroy existing database")

    def kill(self):
        if not self.enable_deploy:
            raise I.KadminException(-1,
                    "Failed to create new database",
                    "This function was disabled")
        import os
        path = '/var/lib/kerberos/krb5kdc'
        for f in os.listdir(path):
            if f.startswith('principal') or f.startswith('.'):
                os.remove(os.path.join(path, f))
        self.realm = None


    def reGenerate(self, password):
        if not self.enable_deploy:
            raise I.KadminException(-1,
                    "Failed to create new database",
                    "This function was disabled")

        _run_command(["kdb5_util", "create", "-s", "-P", password],
               "Failed to create database")
        self.realm = None


def wrap(method):
    @functools.wraps(method)
    def wrapper(self, *args):
        with self._kdb.lock:
            return method(self, self._kdb.kadmin(args[-1]), *args)
    return wrapper



class KadminService(ICore.Service):
    def __init__(self, kdb):
        self._kdb = kdb

    def getName(self, current):
        return 'Kadmin5'


    def isConfigured(self, current):
        try:
            self._kdb.kadmin(None)
            return True
        except Exception:
            return False

    def configure(self, params, current):
        if not self._kdb.enable_deploy:
            raise ICore.RunimeError("Deployment was disabled")
        with self._kdb.lock:
            if 'force' in params:
                try:
                    self._kdb.remove()
                except ICore.Error:
                    self._kdb.kill()
            p = params.get('password')
            if not p:
                raise ICore.ConfigError(
                        'Mandatory parameter not supplied', 'password')
            self._kdb.reGenerate(p)

