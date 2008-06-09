
import Tartarus
from Ice import ServantLocator
from Tartarus import logging

import Tartarus.iface.DNS as I

import db, utils

class Locator(ServantLocator):
    def __init__(self):
        self.obj = ZoneI();
    def locate(self, current):
        return self.obj, None
    def finished(self, current, obj, cookie):
        pass
    def deactivate(self, category):
        pass


class ZoneI(I.Zone):
    def _check_existance(self, con, current):
        cur = utils.execute(con,
            "SELECT count(*) FROM domains WHERE id=%s",
            utils.name(current))
        res = cur.fetchone()[0]
        if res != 1:
            raise utils.NoSuchObject

    def getName(self, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con,
                    "SELECT name FROM domains WHERE id=%s",
                    utils.name(current))
            result = cur.fetchall()
            if len(result) != 1:
                raise utils.NoSuchObject
            return result[0][0]
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while retrieving domain name",
                    e.message)


    _add_record_query = """
    INSERT INTO records (domain_id, name, type, content, ttl, prio)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    def addRecord(self, r, current):
        try:
            con = db.get_connection()
            self._check_existance(con, current)
            id = utils.name(current)
            cur = utils.execute(con,
                    self._add_record_query,
                    id, r.name, str(r.type), r.data,
                    (r.ttl if r.ttl > 0 else None),
                    (r.prio if r.prio >= 0 else None)
                    )
            if cur.rowcount != 1:
                raise utils.NoSuchObject
            con.commit()
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while adding record",
                    e.message)

    def addRecords(self, rs, current):
        try:
            con = db.get_connection()
            self._check_existance(con, current)
            if len(rs) < 1:
                return
            id = utils.name(current)
            rgen = ( (id, r.name, str(r.type), r.data,
                        (r.ttl if r.ttl > 0 else None),
                        (r.prio if r.prio >= 0 else None))
                    for r in rs)
            cur = utils.executemany(con, self._add_record_query, rgen)
            con.commit()
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while adding multiple records",
                    e.message)

    def clearAll(self, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con,
                    "DELETE FROM records WHERE domain_id=%s AND type!='SOA'",
                    utils.name(current))
            if cur.rowcount == 0:
                # no records were deleted. maybe such domain doesn't exist?
                self._check_existance(con, current)
            con.commit()
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while removing all domain records",
                    e.message)

    def dropRecord(self, r, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con,
                    "DELETE FROM records "
                    "WHERE domain_id=%s, name=%s, type=%s, contents=%s",
                    utils.name(current), r.name, str(r.type), r.data)
            if cur.rowcount == 0:
                self._check_existance(con, current)
                #no exception raised - zone exists, but no such record
                raise I.ObjectNotFound("No such record.")
            con.commit()
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while removing records",
                    e.message)


    def countRecords(self, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con,
                "SELECT count(*) FROM records "
                "WHERE domain_id=%s AND type!='SOA'",
                utils.name(current))
            result = cur.fetchone()[0]
            if result == 0:
                self._check_existance(con, current)
            return long(result)
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while counting records",
                    e.message)

    def _unpack_records(self, qresult):
        return [ I.Record(
                        name=n,
                        type=I.RecordType.__dict__[t],
                        data=c,
                        ttl=(ttl if ttl else -1),
                        prio=(prio if prio else -1)
                        )
                 for n, t, c, ttl, prio in qresult
               ]

    def getRecords(self, limit, offset, current):
        try:
            con = db.get_connection()
            #self._check_existance(con, current)

            cur = utils.execute_limited(con, limit, offset,
                    "SELECT name, type, content, ttl, prio "
                    "FROM records WHERE domain_id=%s AND type != 'SOA'",
                    utils.name(current))
            res = cur.fetchall()
            return self._unpack_records(res)
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while fetching records",
                    e.message)

    def findRecords(self, phrase, limit, current):
        try:
            con = db.get_connection()
            self._check_existance(con, current)

            cur = utils.execute_limited(con, limit, 0,
                    "SELECT name, type, content, ttl, prio FROM records "
                    "WHERE domain_id=%s AND type!='SOA' AND name LIKE %s",
                    utils.name(current), phrase)
            return self._unpack_records(cur.fetchall())
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while fetching records",
                    e.message)

    def getSOA(self, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con,
                    "SELECT content FROM records "
                    "WHERE type='SOA' and domain_id=%s",
                    utils.name(current))
            res = cur.fetchall()
            if len(res) != 1:
                raise utils.NoSuchObject
            return I.SOARecord(*utils.str2soar(res[0][0]))
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while retrieving domain name",
                    e.message)

    def setSOA(self, soar, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con,
                    "UPDATE records SET content=%s "
                    "WHERE type='SOA' and domain_id=%s",
                    utils.soar2str(soar), utils.name(current))
            if cur.rowcount != 1:
                raise db.NoSuchObject
            con.commit()
        except db.module.Error, e:
            raise I.DBError(
                    "Database failure while setting SOA record",
                    e.message)

