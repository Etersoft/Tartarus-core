
from __future__ import with_statement

import kadmin5, Tartarus, threading, functools, subprocess, IceSSL

import Tartarus.iface.Kerberos as I
import Tartarus.iface.core as C

from os import errno
from kadmin5 import kadm_errors as ke

_AUTH_ERRORS = set([
        errno.EACCES,
        errno.EPERM,
        ke.KADM5_AUTH_ADD,
        ke.KADM5_AUTH_CHANGEPW,
        ke.KADM5_AUTH_DELETE,
        ke.KADM5_AUTH_GET,
        ke.KADM5_AUTH_INSUFFICIENT,
        ke.KADM5_AUTH_LIST,
        ke.KADM5_AUTH_MODIFY,
        ke.KADM5_AUTH_SETKEY
    ])

_NOTFOUND_ERRORS = set([
        ke.KADM5_UNK_POLICY,
        ke.KADM5_UNK_PRINC
    ])

_ALREADYEXISTS_ERRORS = [
        ke.KADM5_DUP
        ]


class KadmExcCallback(object):
    def __init__(self, princ):
        self.princ = princ

    def __call__(self, code, where, message):
        if code in _ALREADYEXISTS_ERRORS:
            raise C.AlreadyExistsError(message, where)
        if code in _AUTH_ERRORS:
            raise C.PermissionError(message, where, self.princ)
        if code in _NOTFOUND_ERRORS:
            raise C.NotFoundError(message, where)
        raise I.KadminError(message, where, code)



def _run_command(args, msg):
    try:
        p = subprocess.Popen(args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        res = p.wait()
        s = p.communicate()[1]
        if res != 0:
            raise C.RuntimeError(s)
    except OSError, e:
        raise C.RuntimeError(msg + ': ' + e.strerror)


class Kdb(object):
    def __init__(self, enable_deploy, realm=None):
        self.lock = threading.Lock()
        self.realm = realm
        self.enable_deploy = enable_deploy

    def kadmin(self, current):
        try:
            princ = IceSSL.getConnectionInfo(current.con).krb5Princ
            # we need to transform princ@REALM to princ/admin@REALM
            # for simplicity, we assume REALM part does not contain
            # '@' character
            ind = princ.rfind('@')
            if ind > 0:
                if not princ[:ind].endswith("/admin"):
                    aprinc = princ[:ind] + "/admin" + princ[ind:]
            else:
                aprinc = "unknown/admin"
        except Exception:
            princ = "unknown"
            aprinc = "Tartarus/admin"

        result = kadmin5.kadmin(error_cb=KadmExcCallback(princ),
                                princname=aprinc, realm=self.realm)
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


class KadminService(C.Service):
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
            raise C.RunimeError("Deployment was disabled")
        with self._kdb.lock:
            if 'force' in params:
                try:
                    self._kdb.remove()
                except C.Error:
                    self._kdb.kill()
            p = params.get('password')
            if not p:
                raise C.ConfigError(
                        'Mandatory parameter not supplied', 'password')
            self._kdb.reGenerate(p)

