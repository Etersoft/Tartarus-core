
import Tartarus
from Ice import ServantLocator
from Tartarus import logging, db

import Tartarus.iface.DNS as I

import utils

class Locator(ServantLocator):
    def __init__(self, dbh):
        self.obj = ZoneI(dbh);
    def locate(self, current):
        return self.obj, None
    def finished(self, current, obj, cookie):
        pass
    def deactivate(self, category):
        pass


class ZoneI(I.Zone):
    def __init__(self, dbh):
        # db.wrap expects database helper to be here:
        self._dbh = dbh

    def _get_name(self, con, current):
        cur = self._dbh.execute(con,
                "SELECT name FROM domains WHERE id=%s",
                utils.name(current))
        result = cur.fetchall()
        if len(result) != 1:
            raise utils.NoSuchObject
        return result[0][0]

    def _check_existance(self, con, current):
        self._get_name(con, current)

    @db.wrap("getting zone name")
    def getName(self, con, current):
        return self._get_name(con, current)


    _add_record_query = """
    INSERT INTO records (domain_id, name, type, content, ttl, prio)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    def _unpack_record(self, r, id, domain):
        if r.name.endswith('.'):
            r.name = r.name[:-1]
        #if not r.name.endswith(domain):
        #    raise ICore.ValueError('Invalid record name.', r.name)
        return (id, r.name, str(r.type), r.data,
                (r.ttl if r.ttl > 0 else None),
                (r.prio if r.prio >= 0 else None))

    @db.wrap("adding record")
    def addRecord(self, con, r, current):
        domain = self._get_name(con, current)
        id = utils.name(current)
        cur = self._dbh.execute(con,
                self._add_record_query,
                *self._unpack_record(r, id, domain)
               )
        if cur.rowcount != 1:
            raise utils.NoSuchObject
        con.commit()

    @db.wrap("adding records")
    def addRecords(self, con, rs, current):
        domain = self._get_name(con, current)
        if len(rs) < 1:
            return
        id = utils.name(current)
        rgen = (self._unpack_record(r,id, domain) for r in rs)
        cur = self._dbh.execute_many(con, self._add_record_query, rgen)
        con.commit()

    @db.wrap("removing all records of a zone")
    def clearAll(self, con, current):
        cur = self._dbh.execute(con,
                "DELETE FROM records WHERE domain_id=%s AND type!='SOA'",
                utils.name(current))
        if cur.rowcount == 0:
            # no records were deleted. maybe such domain doesn't exist?
            self._check_existance(con, current)
        con.commit()

    @db.wrap("removing record")
    def dropRecord(self, con, r, current):
        if r.name.endswith('.'):
            r.name = r.name[:-1]
        cur = self._dbh.execute(con,
                "DELETE FROM records "
                "WHERE domain_id=%s AND name=%s AND type=%s AND content=%s",
                utils.name(current), r.name, str(r.type), r.data)
        if cur.rowcount == 0:
            self._check_existance(con, current)
            #no exception raised - zone exists, but no such record
            raise ICore.NotFoundError("No such record.")
        con.commit()

    @db.wrap("replacing record")
    def replaceRecord(self, con, oldr, newr, current):
        domain = self._get_name(con, current)
        if oldr.name.endswith('.'):
            oldr.name = oldr.name[:-1]
        args = self._unpack_record(newr, None, domain)[1:]
        args += (utils.name(current), oldr.name, str(oldr.type), oldr.data)
        cur = self._dbh.execute(con,
                "UPDATE records SET "
                "name=%s, type=%s, content=%s, ttl=%s, prio=%s "
                "WHERE domain_id=%s AND name=%s AND type=%s AND content=%s",
                *args)
        if cur.rowcount != 1:
            # domain already exists, so there is no such record
            raise ICore.NotFoundError("Failed to replace record",
                    "Record not found")
        con.commit()


    @db.wrap("counting records")
    def countRecords(self, con, current):
        cur = self._dbh.execute(con,
            "SELECT count(*) FROM records "
            "WHERE domain_id=%s AND type!='SOA'",
            utils.name(current))
        result = cur.fetchone()[0]
        if result == 0:
            self._check_existance(con, current)
        return long(result)

    def _pack_records(self, qresult):
        return [ I.Record(
                        name=n,
                        type=I.RecordType.__dict__[t],
                        data=c,
                        ttl=(ttl if ttl else -1),
                        prio=(prio if prio else -1)
                        )
                 for n, t, c, ttl, prio in qresult
               ]

    @db.wrap("retrieving records")
    def getRecords(self, con, limit, offset, current):
        cur = self._dbh.execute_limited(con, limit, offset,
                "SELECT name, type, content, ttl, prio "
                "FROM records WHERE domain_id=%s AND type != 'SOA'",
                utils.name(current))
        res = cur.fetchall()
        if len(res) < 1:
            #maybe there is no such zone?
            self._check_existance(con, current)
        return self._pack_records(res)

    @db.wrap("retrieving records")
    def findRecords(self, con, phrase, limit, current):
        phrase = (phrase.replace('\\',  '\\\\')
                        .replace('%',   '\\%')
                        .replace('_',   '\\_')
                        + '%')
        cur = self._dbh.execute_limited(con, limit, 0,
                "SELECT name, type, content, ttl, prio FROM records "
                "WHERE domain_id=%s AND type!='SOA' AND name LIKE %s",
                utils.name(current), phrase)
        res = cur.fetchall()
        if len(res) < 1:
            #maybe there is no such zone?
            self._check_existance(con, current)
        return self._pack_records(res)

    @db.wrap("retrieving SOA record")
    def getSOA(self, con, current):
        cur = self._dbh.execute(con,
                "SELECT content FROM records "
                "WHERE type='SOA' and domain_id=%s",
                utils.name(current))
        res = cur.fetchall()
        if len(res) != 1:
            raise utils.NoSuchObject
        return I.SOARecord(*utils.str2soar(res[0][0]))

    @db.wrap("setting SOA record")
    def setSOA(self, con, soar, current):
        cur = self._dbh.execute(con,
                "UPDATE records SET content=%s "
                "WHERE type='SOA' and domain_id=%s",
                utils.soar2str(soar), utils.name(current))
        if cur.rowcount != 1:
            raise db.NoSuchObject
        con.commit()

