
import Tartarus
from Tartarus import logging
import Tartarus.iface.DNS as I

import db
import db_create
import proxy

class ServerI(I.Server):
    def getDomains(self, current):
        try:
            con = db.get_connection()
            cur = con.cursor()
            cur.execute('SELECT id FROM domains')
            result = [ proxy.create(I.DomainPrx, current, "DNS-Domain", x[0])
                       for x in cur.fetchall() ];
            return result
        except db.module.Error, e:
            raise I.Errors.DBError("Database failure", e.message)

    def getDomain(self, name, current):
        try:
            result = db.fetch_one(db.get_connection(),
                    'SELECT id FROM domains WHERE name=%(name)s',
                    name=name)
            return proxy.create(I.DomainPrx, current, "DNS-Domain", result[0])
        except db.module.Error, e:
            raise I.Errors.DBError("Database failure", e.message)

    def createDomain(self, name, current):
        try:
            con = db.get_connection()
            con.cursor().execute(
                    'INSERT INTO domains (name, type) '
                    'values (%(name)s, %(type)s)',
                    {'name' : name, 'type' : 'NATIVE'})
            con.commit()
        except db.module.Error, e:
            raise I.Errors.DBError("Domain creation failed", e.message)

    def _dropDomain(self, id):
        try:
            con = db.get_connection()
            cur = con.cursor()
            cur.execute(
                    "DELETE FROM domains WHERE id=%(id)s", {'id': id})
            if cur.rowcount != 1:
                raise I.Error.ObjectNotFound("Domain not found in database")
            con.cursor().execute(
                    "DELETE FROM records WHERE domain_id=%(id)s", {'id': id})
            con.commit()
        except db.module.Error, e:
            raise I.Errors.DBError("Domain delition failed", e.message)

    def deleteDomain(self, name, current):
        id = db.fetch_one(db.get_connection(),
                "SELECT id FROM domains WHERE name=%(n)s", n=name)[0]
        self._dropDomain(id)

    def deleteDomainByRef(self, proxy, current):
        id = proxy.ice_getIdentity().name
        self._dropDomain(id)

    def getOptions(self, current):
        return I.ServerOptionSeq()

    def setOptions(self, opts, current):
        if len(opts) < 1:
            return
        raise I.Errors.ValueError("Unsupported option", opts[0].name)

    def setOption(self, opt, current):
        raise I.Errors.ValueError("Unsupported option", opt.name)

    def initNewDatabase(self, current):
        db_create.create_db()

