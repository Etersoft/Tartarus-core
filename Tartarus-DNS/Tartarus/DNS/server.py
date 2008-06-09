
import Tartarus
from Tartarus import logging
import Tartarus.iface.DNS as I

import db
import db_create
import utils

class ServerI(I.Server):
    def getZones(self, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con, 'SELECT id FROM domains')
            result = [ utils.proxy(I.ZonePrx, current, "DNS-Zone", str(x[0]))
                       for x in cur.fetchall() ];
            return result
        except db.module.Error, e:
            raise I.DBError("Database failure", e.message)

    def getZone(self, name, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con,
                    'SELECT id FROM domains WHERE name=%s',name)
            result = cur.fetchall()
            if len(result) != 1:
                raise I.ObjectNotFound("Could not locate zone in the database")
            return utils.proxy(I.ZonePrx, current, "DNS-Zone", str(result[0][0]))
        except db.module.Error, e:
            raise I.DBError("Database failure", e.message)

    def createZone(self, name, soar, current):
        try:
            con = db.get_connection()
            utils.execute(con,
                    'INSERT INTO domains (name, type) VALUES (%s, %s)',
                    name, 'NATIVE')
            con.commit()
        except db.module.Error, e:
            raise I.DBError("Zone creation failed", e.message)

    def _dropZone(self, con, id):
        try:
            cur = utils.execute(con,
                    "DELETE FROM domains WHERE id=%s", id)
            if cur.rowcount != 1:
                raise I.ObjectNotFound("Zone not found in database.")
            utils.execute(con,
                    "DELETE FROM records WHERE domain_id=%s", id)
            con.commit()
        except db.module.Error, e:
            raise I.DBError("Zone delition failed", e.message)

    def deleteZone(self, name, current):
        con = db.get_connection()
        id = None
        try:
            cur = utils.execute(con,
                    "SELECT id FROM domains WHERE name=%s", name)
            res = cur.fetchall()
            if len(res) != 1:
                raise I.ObjectNotFound("No such zone.")
            id = res[0][0]
        except db.module.Error, e:
            raise I.DBError("Database failure.", e.message)
        self._dropZone(con, id)

    def deleteZoneByRef(self, proxy, current):
        id = utils.name(current, proxy.ice_getIdentity())
        self._dropZone(db.get_connection(), id)

    def getOptions(self, current):
        return I.ServerOptionSeq()

    def setOptions(self, opts, current):
        if len(opts) < 1:
            return
        raise I.ValueError("Unsupported option", opts[0].name)

    def setOption(self, opt, current):
        raise I.ValueError("Unsupported option", opt.name)

    def initNewDatabase(self, current):
        db_create.create_db()

