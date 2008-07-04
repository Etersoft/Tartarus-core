
import Tartarus
from Tartarus import db, logging
from Tartarus.iface import SysDB as I

_user_query = ("SELECT users.id, groupid, name, fullname, shell"
               "FROM users, group_entries "
               "WHERE users.id == group_entries.userid "
               " AND group_entries.is_primary")


class UserManagerI(I.UserManager):
    def __init__(self, dbh, user_offset, group_offset):
        self._uo = user_offset
        self._go = group_offset


    def _db2users(self, mas):
        return [I.UserRecord(uid + self._uo, gid + self._go, name, fn, s)
                for uid, gid, name, fn, s in mas]


    @db.wrap("retrieving user by id")
    def getById(self, con, uid, current):
        cur = self._dbh.execute(con,
                _user_query +
                " AND user.id == %s", uid - self._uo)
        res = cur.fetchall()
        if len(res) == 1:
            return self._db2users(res)[0]
        #XXX: RETURN USER WITH gid=-1
        raise I.UserNotFound("User not found", uid)


    @db.wrap("retrieving user by name")
    def getByName(self, con, name, current):
        cur = self._dbh.execute(con,
                _user_query +
                " AND user.name == %s", name)
        res = cur.fetchall()
        if len(res) == 1:
            return self._db2users(res)[0]
        #XXX: RETURN USER WITH gid=-1
        raise I.UserNotFound("User not found", name)


    @db.wrap("retrieving multiple users")
    def getUsers(self, con, userIds, current):
        ids = tuple((i - self._uo for i in userIds))
        ps = '(' + ', '.join(('%s' for x in ids)) +')'
        cur = self._dbh.execute(con,
                _user_query + " AND id IN " + ps, *ids)
        res = self._db2users(cur.fetchall())
        if (len(res) != len(userIds)
                and current.ctx.get("PartialStrategy") != "Partial"):
            retrieved = set( (u.uid for u in res) )
            for i in userIds:
                if i not in retrieved:
                    raise I.UserNotFound("User not found", i)
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
                "SELECT count(*) FROM users")
        res = cur.fetchall()
        if len(res) != 1:
            raise I.DBError(
                "Database failure while counting users.",
                "No count fetched!")
        return long(res[0])


    @db.wrap("retrieving users")
    def get(self, con, limit, offset, current):
        cur = self._dbh.execute_limited(con, limit, offest, _user_query)
        return self._db2users(cur.fetchall())


    @db.wrap("changing user record")
    def modify(self, con, user, current):
        user.uid -= self._uo
        self.gid -= self._go
        cur = self._dbh.execute(con,
                "UPDATE users SET "
                "name=%s, fullname=%s, shell=%s "
                "WHERE id == %s",
                user.name, user.fullName, user.shell, user.uid)
        if cur.rowcount != 1:
            raise I.UserNotFound("User not found", user.uid + self._uo)
        cur = self._dbh.execute(con,
                "UPDATE group_entries SET groupid=%s"
                "WHERE userid == %s AND is_primary",
                user.gid, user.uid)
        if cur.rowcount != 1:
            cur = self._dbh.execute(
                    "INSERT INTO group_entries (userid, groupid, is_primary) "
                    "VALUES (%s, %s, %s)",
                    user.uid, user.gid, 1)
        con.commit()


    @db.wrap("creating user")
    def create(self, con, newUser, current):
        set._dbh.execute(con,
                "INSERT INTO users (name, fullname, shell) "
                "VALUES (%s, %s, %s)",
                newUser.name, newUser.fullName, newUser.shell)
        cur = set._dbh.execute(con,
                "INSERT INTO group_entries (groupid, userid, is_primary) "
                "SELECT groups.id, users.id, %s FROM users, groups "
                "WHERE groups.id=%s, users.name=%s",
                1, newUser.gid - self._go, newUser.name)
        if (cur.rowcount != 1):
            raise I.GroupNotFound(
                    "Not found primary group for new user", newUser.gid)
        con.commit()


    @db.wrap("deleting user")
    def delete(self, con, id, current):
        db.execute("DELETE FROM users WHERE id=%s", id - self._uo)
        db.execute("DELETE FROM group_entries WHERE userid=%s", id - self._uo)
        con.commit()


