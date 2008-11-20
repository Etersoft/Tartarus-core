
import Tartarus
from Tartarus import db, logging
from Tartarus.iface import SysDB as I
from Tartarus.iface import core as ICore

_user_query = ("SELECT users.id, groupid, name, fullname, shell "
               "FROM users , group_entries "
               "WHERE users.id == group_entries.userid "
               "AND group_entries.is_primary ")


class UserManagerI(I.UserManager):
    def __init__(self, dbh, user_offset, group_offset):
        self._dbh = dbh
        self._uo = user_offset
        self._go = group_offset


    def _db2users(self, mas):
        return [I.UserRecord(uid + self._uo, gid + self._go, str(name),
                            (str(fn) if fn else ""), str(s))
                for uid, gid, name, fn, s in mas]


    @db.wrap("retrieving user by id")
    def getById(self, con, uid, current):
        cur = self._dbh.execute(con,
                _user_query +
                " AND users.id == %s", uid - self._uo)
        res = cur.fetchall()
        if len(res) == 1:
            return self._db2users(res)[0]
        #XXX: RETURN USER WITH gid=-1
        raise I.UserNotFound("User not found",
                "retrieving user by id", uid)


    @db.wrap("retrieving user by name")
    def getByName(self, con, name, current):
        cur = self._dbh.execute(con,
                _user_query +
                " AND users.name == %s", name)
        res = cur.fetchall()
        if len(res) == 1:
            return self._db2users(res)[0]
        #XXX: RETURN USER WITH gid=-1
        raise I.UserNotFound("User not found",
                "retrieving data for user %s" % name, -1)


    @db.wrap("retrieving multiple users")
    def getUsers(self, con, userids, current):
        ids = tuple((i - self._uo for i in userids))
        ps = '(' + ', '.join(('%s' for x in ids)) +')'
        cur = self._dbh.execute(con,
                _user_query + " AND users.id IN " + ps, *ids)
        res = self._db2users(cur.fetchall())
        if (len(res) != len(userids)
                and current.ctx.get("PartialStrategy") != "Partial"):
            retrieved = set( (u.uid for u in res) )
            for i in userids:
                if i not in retrieved:
                    raise I.UserNotFound("User not found",
                            "retrieving multiple users", i)
        return res


    @db.wrap("searching for users")
    def search(self, con, factor, limit, current):
        phrase = (factor.replace('\\',  '\\\\')
                        .replace('%',   '\\%')
                        .replace('_',   '\\_')
                        + '%')
        cur = self._dbh.execute_limited(con, limit, 0,
                _user_query +
                " AND (name LIKE %s or fullname LIKE %s)",
                phrase, phrase)
        return self._db2users(cur.fetchall())


    @db.wrap("counting users")
    def count(self, con, current):
        cur = self._dbh.execute(con,
                "SELECT count(name) FROM users")
        res = cur.fetchall()
        if len(res) != 1:
            raise ICore.DBError(
                "Database failure while counting users.",
                "No count fetched!")
        return long(res[0][0])


    @db.wrap("retrieving users")
    def get(self, con, limit, offset, current):
        cur = self._dbh.execute_limited(con, limit, offset, _user_query)
        return self._db2users(cur.fetchall())


    @db.wrap("changing user record")
    def modify(self, con, user, current):
        uid = user.uid - self._uo
        gid = user.gid - self._go
        cur = self._dbh.execute(con,
                "UPDATE users SET "
                "name=%s, fullname=%s, shell=%s "
                "WHERE id == %s",
                user.name, user.fullName, user.shell, uid)
        if cur.rowcount != 1:
            raise I.UserNotFound("User not found",
                    "changing user record", user.uid)
        cur = self._dbh.execute(con,
                "UPDATE group_entries SET groupid=%s"
                "WHERE userid == %s AND is_primary",
                gid, uid)
        if cur.rowcount != 1:
            cur = self._dbh.execute(
                    "INSERT INTO group_entries (userid, groupid, is_primary) "
                    "VALUES (%s, %s, %s)",
                    uid, gid, 1)
        con.commit()


    @db.wrap("creating user")
    def create(self, con, newuser, current):
        if len(newuser.shell) == 0:
            newuser.shell = "/bin/bash" # hardcoded default, yeah...
        self._dbh.execute(con,
                "INSERT INTO users (name, fullname, shell) "
                "VALUES (%s, %s, %s)",
                newuser.name, newuser.fullName, newuser.shell)
        cur = self._dbh.execute(con,
                "SELECT id FROM users WHERE name = %s", newuser.name)
        res = cur.fetchall()
        if len(res) != 1:
            raise ICore.DBError("Failed to add user",
                    "User not found after insertion")
        uid = res[0][0]
        cur = self._dbh.execute(con,
                "INSERT INTO group_entries (groupid, userid, is_primary) "
                "SELECT groups.id, %s, %s FROM groups WHERE groups.id=%s",
                uid, 1, newuser.gid - self._go)
        if (cur.rowcount != 1):
            raise I.GroupNotFound("Group not found",
                    "Could not find primary group for new user", newuser.gid)
        con.commit()
        return uid + self._uo

    @db.wrap("deleting user")
    def delete(self, con, uid, current):
        cur = self._dbh.execute(con,
                "DELETE FROM users WHERE id=%s", uid - self._uo)
        if cur.rowcount != 1:
            raise I.UserNotFound("User not found", "deleting user", uid)
        self._dbh.execute(con,
                "DELETE FROM group_entries WHERE userid=%s",
                uid - self._uo)
        con.commit()


