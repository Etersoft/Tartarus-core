
import Tartarus, Ice
from Tartarus import logging
import Tartarus.iface.DNS as I

import db

class Locator(Ice.ServantLocator):
    def __init__(self):
        self.obj = DomainI();
    def locate(self, current):
        return self.obj, None
    def finished(self, current, obj, cookie):
        pass
    def deactivate(self, category):
        pass


class DomainI(I.Domain):
    def getName(self, current):
        try:
            return db.fetch_one(db.get_connection(),
                    "SELECT name FROM domains WHERE id=%(id)s",
                    current,
                    id=current.id.name)[0]
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while retrieving domain name",
                    e.message)


    _add_record_query = """
    INSERT INTO records (domain_id, name, type, content, ttl, prio)
    SELECT id, %(name)s, %(type)s, %(content)s, %(ttl)s, %(prio)s
    WHERE id=%(id)s
    """

    def _record_to_dict(self, r, **params):
        res = params
        res['name'] = r.name
        res['content'] = r.content
        res['type'] = str(r.type)
        res['ttl'] = (None if r.ttl == -1 else r.ttl)
        res['prio'] = (None if r.prio == -1 else r.prio)
        return res

    def addRecord(self, r, current):
        try:
            con = db.get_connection()
            con.cursor().execute(self._add_record_query,
                    self._record_to_dict(r, id=current.id.name))
            con.commit()
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while adding record",
                    e.message)

    def addRecords(self, rs, current):
        try:
            if len(rs) < 1:
                return
            con = db.get_connection()
            records = [self._record_to_dict(r, id=current.id.name)
                       for r in rs]
            con.cursor().executemany(self._add_record_query, records)
            con.commit()
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while adding multiple records",
                    e.message)


    def clearAll(self, current):
        try:
            con = db.get_connection()
            con.cursor().execute(
                    "DELETE FROM records WHERE domain_id = %(id)s",
                    {'id': current.id.name})
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while removing all domain records",
                    e.message)

    def dropRecord(self, r, current):
        try:
            con = db.get_connection()
            con.cursor().execute("DELETE FROM records "
                    "WHERE domain_id = %(id)s, name=%(name), "
                        "type=%(rt), contents=%(rc) ",
                    self._record_to_dict(r, id=current.id.name))
            con.commit()
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while removing records",
                    e.message)


    def countRecords(self, current):
        try:
            con = db.get_connection()
            cur = con.cursor()
            cur.execute(
                "SELECT count(*) FROM records WHERE domain_id=%(id)s",
                {'id' : current.id.name})
            result = cur.fetchone()[0]
            return long(result)
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while removing records",
                    e.message)

    def _unpack_records(self, qresult):
        return [ I.Record(
                        name=n,
                        type=I.RecordType.__dict__[t],
                        content=c,
                        ttl=(ttl if ttl else -1),
                        prio=(prio if prio else -1)
                        )
                 for n, t, c, ttl, prio in qresult
               ]

    def getRecords(self, limit, offset, current):
        try:
            con = db.get_connection()
            cur = con.cursor()

            q = ""
            if limit > 0:
                q = "LIMIT %(limit)s"
                if offset > 0:
                    q += "OFFSET %(offset)s"

            cur.execute(
                    "SELECT name, type, content, ttl, prio "
                    "FROM records WHERE domain_id=%(id)s " + q,
                    {'id':current.id.name, 'limit':limit, 'offset':offset})
            return self._unpack_records(cur.fetchall())
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while fetching records",
                    e.message)

    def findRecords(self, phrase, limit, current):
        try:
            con = db.get_connection()
            cur = con.cursor()

            q = ""
            if limit > 0:
                q = "LIMIT %(limit)s"

            cur.execute(
                    "SELECT name, type, content, ttl, prio "
                    "FROM records WHERE domain_id=%(id)s"
                    "AND name LIKE %(pat)s" + q,
                    {'id':current.id.name, 'pat':phrase, 'limit':limit})
            return self._unpack_records(cur.fetchall())
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while fetching records",
                    e.message)

    def getSOA(self, current):
        try:
            result = db.fetch_one(db.get_connection(),
                    "SELECT content FROM records "
                    "WHERE type='SOA' and domain_id=%(id)s",
                    id=current.id.name)[0]
            (pr, hm, s, ref, ret, exp, dt) = result.split()
            return I.SOARecord(pr, hm,
                        long(s), long(ref), long(ret),
                        long(exp), long(dt))
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while retrieving domain name",
                    e.message)


    def setSOA(self, soar, current):
        try:
            con = db.get_connection()
            con.cursor().execute("DELETE FROM records "
                    "WHERE type='SOA' AND domain_id=%(id)s",
                    {'id':current.id.name})

            str = ('%(primary)s %(hostmaster)s %(serial)d %(refresh)d '
                   '%(retry)d %(expire)d %(defaultTtl)d' % soar.__dict__)
            cur = con.cursor()
            cur.execute(
                    "INSERT INTO records (domain_id, name, type, content) "
                    "SELECT id, name, 'SOA', %(cont)s "
                    "FROM domains WHERE id=%(id)s",
                    {'cont':str, 'id':current.id.name})
            if cur.rowcount != 1:
                raise db.NoSuchObject
            con.commit()
        except db.module.Error, e:
            raise I.Errors.DBError(
                    "Database failure while setting SOA record",
                    e.message)



