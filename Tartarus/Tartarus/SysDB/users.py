
import Tartarus, re, pwd
from Tartarus import db, logging, auth
from Tartarus.iface import SysDB as I
from Tartarus.iface import core as C


_user_query = "SELECT uid, gid, name, fullname, shell FROM users "

_GOOD_USER_NAME = "[A-Za-z].*"


class UserManagerI(I.UserManager):
    def __init__(self, dbh, user_offset, group_offset):
        self._dbh = dbh
        self._uo = user_offset
        self._go = group_offset
        self._good_name = re.compile(_GOOD_USER_NAME)


    def _db2users(self, mas):
        return [I.UserRecord(uid + self._uo, gid + self._go, str(name),
                            (str(fn) if fn else ""), str(s))
                for uid, gid, name, fn, s in mas]


    @auth.mark('read')
    @db.wrap("retrieving user by id")
    def getById(self, con, uid, current):
        cur = self._dbh.execute(con,
                _user_query +
                " WHERE uid == %s", uid - self._uo)
        res = cur.fetchall()
        if len(res) == 1:
            return self._db2users(res)[0]
        #XXX: RETURN USER WITH gid=-1
        raise I.UserNotFound("User not found",
                "retrieving user by id", uid)


    @auth.mark('read')
    @db.wrap("retrieving user by name")
    def getByName(self, con, name, current):
        cur = self._dbh.execute(con,
                _user_query +
                " WHERE users.name == %s", name)
        res = cur.fetchall()
        if len(res) == 1:
            return self._db2users(res)[0]
        #XXX: RETURN USER WITH gid=-1
        raise I.UserNotFound("User not found",
                "retrieving data for user %s" % name, -1)

    @auth.mark('read')
    @db.wrap("retrieving multiple users")
    def getUsers(self, con, userids, current):
        ids = tuple((i - self._uo for i in userids))
        ps = '(' + ', '.join(('%s' for x in ids)) +')'
        cur = self._dbh.execute(con,
                _user_query + " WHERE uid IN " + ps, *ids)
        res = self._db2users(cur.fetchall())
        if (len(res) != len(userids)
                and current.ctx.get("PartialStrategy") != "Partial"):
            retrieved = set( (u.uid for u in res) )
            for i in userids:
                if i not in retrieved:
                    raise I.UserNotFound("User not found",
                            "retrieving multiple users", i)
        return res


    @auth.mark('read')
    @db.wrap("searching for users")
    def search(self, con, factor, limit, current):
        phrase = (factor.replace('\\',  '\\\\')
                        .replace('%',   '\\%')
                        .replace('_',   '\\_')
                        + '%')
        cur = self._dbh.execute_limited(con, limit, 0,
                _user_query +
                " WHERE (name LIKE %s ESCAPE '\\'"
                " OR fullname LIKE %s ESCAPE '\\')",
                phrase, phrase)
        return self._db2users(cur.fetchall())


    @auth.mark('read')
    @db.wrap("counting users")
    def count(self, con, current):
        cur = self._dbh.execute(con,
                "SELECT count(*) FROM users")
        res = cur.fetchall()
        if len(res) != 1:
            raise C.DBError(
                "Database failure while counting users.",
                "No count fetched!")
        return long(res[0][0])


    @auth.mark('read')
    @db.wrap("retrieving users")
    def get(self, con, limit, offset, current):
        cur = self._dbh.execute_limited(con, limit, offset, _user_query)
        return self._db2users(cur.fetchall())


    @auth.mark('write')
    @db.wrap("changing user record")
    def modify(self, con, user, current):
        if not self._good_name.match(user.name):
            raise C.ValueError("Invalid user name: %s" % user.name)
        uid = user.uid - self._uo
        gid = user.gid - self._go
        try:
            cur = self._dbh.execute(con,
                    "UPDATE users SET "
                    "name=%s, gid=%s, fullname=%s, shell=%s "
                    "WHERE uid == %s",
                    user.name, gid, user.fullName, user.shell, uid)
        except self._dbh.IntegrityError:
            raise C.AlreadyExistsError("User already exists",
                                       user.name)
        if cur.rowcount != 1:
            raise I.UserNotFound("User not found",
                    "changing user record", user.uid)
        con.commit()


    @auth.mark('write')
    @db.wrap("creating user")
    def create(self, con, newuser, current):
        if not self._good_name.match(newuser.name):
            raise C.ValueError("Invalid user name: %s" % newuser.name)
        try:
            pwd.getpwnam(newuser.name)
        except KeyError:
            pass
        else:
            raise C.ValueError("Current site policy does not allow to "
                               "create users that already exist on server",
                               newuser.name)
        if len(newuser.shell) == 0:
            newuser.shell = None
        try:
            self._dbh.execute(con,
                    "INSERT INTO users (name, gid, fullname, shell) "
                    "VALUES (%s, %s, %s, %s)",
                    newuser.name, newuser.gid - self._go,
                    newuser.fullName, newuser.shell)
        except self._dbh.IntegrityError:
            raise C.AlreadyExistsError("User already exists",
                                       newuser.name)
        cur = self._dbh.execute(con,
                "SELECT uid FROM users WHERE name = %s", newuser.name)
        res = cur.fetchall()
        if len(res) != 1:
            raise C.DBError("Failed to add user",
                            "User not found after insertion")
        con.commit()
        return res[0][0] + self._uo

    @auth.mark('write')
    @db.wrap("deleting user")
    def delete(self, con, uid, current):
        cur = self._dbh.execute(con,
                "DELETE FROM users WHERE uid=%s", uid - self._uo)
        if cur.rowcount != 1:
            raise I.UserNotFound("User not found", "deleting user", uid)
        con.commit()

