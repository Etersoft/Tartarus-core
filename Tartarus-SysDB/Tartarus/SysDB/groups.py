
import Tartarus
from Tartarus import db, logging
from Tartarus.iface import SysDB as I


class GroupManagerI(I.GroupManager):
    def __init__(self, dbh, user_offset, group_offset):
        self._dbh = dbh
        self._uo = user_offset
        self._go = group_offset


    def _db2users(self, mas):
        return [I.UserRecord(uid + self._uo, gid + self._go,
                             str(name), str(fn), s)
                for uid, gid, name, fn, s in mas]


    def _db2groups(self, mas):
        return [I.GroupRecord(gid + self._go, str(name), str(descr))
                for gid, name, descr in mas]

    def _group_exists(self, con, gid):
        cur = self._dbh.execute(con,
                "SELECT name FROM groups WHERE id == %s",
                gid - self._go)
        if len(cur.fetchall()) != 1:
            raise I.GroupNotFound("Group not found", gid)

    def _user_exists(self, con, uid):
        cur = self._dbh.execute(con,
                "SELECT name FROM users WHERE id == %s",
                uid - self._uo)
        if len(cur.fetchall()) != 1:
            raise I.UserNotFound("Group not found", gid)

    @db.wrap("retrieving group by id")
    def getById(self, con, gid, current):
        cur = self._dbh.execute(con,
                "SELECT id, name, description FROM groups "
                "WHERE id == %s", gid - self._go)
        res = cur.fetchall()
        if len(res) != 1:
            raise I.GroupNotFound("Group not found", gid)
        return self._db2groups(res)[0]

    @db.wrap("retrieving group by name")
    def getByName(self, con, name, current):
        cur = self._dbh.execute(con,
                "SELECT id, name, description FROM groups "
                "WHERE name == %s", name)
        res = cur.fetchall()
        if len(res) != 1:
            raise I.NotFound("Group not found: %s" % name)
        return self._db2groups(res)[0]

    @db.wrap("retrieving groups for user id")
    def getGroupsForUserId(self, con, uid, current):
        cur = self._dbh.execute(con,
                "SELECT groups.id "
                "FROM groups, group_entries "
                "WHERE groups.id == group_entries.groupid "
                "AND group_entries.userid == %s",
                uid - self._uo)
        res = cur.fetchall()
        if len(res) == 0:
            #user definitly has primary group...
            raise I.UserNotFound("User not found", uid)
        return [ x[0] + self._go for x in res ]

    @db.wrap("retrieving groups for user name")
    def getGroupsForUserName(self, con, name, current):
        cur = self._dbh.execute(con,
                "SELECT groups.id "
                "FROM groups, group_entries, users "
                "WHERE groups.id == group_entries.groupid "
                "AND group_entries.userid == users.id "
                "AND users.name == %s",
                name)
        res = cur.fetchall()
        if len(res) == 0:
            #user definitly has primary group...
            raise I.UserNotFound("User not found", name)
        return [ x[0] + self._go for x in res ]


    @db.wrap("retrieving multiple groups")
    def getGroups(self, con, groupIds, current):
        ids = tuple((i - self._go for i in groupIds))
        ps = '(' + ', '.join(('%s' for x in ids)) +')'
        cur = self._dbh.execute(con,
                "SELECT id, name, description FROM groups "
                + " AND id IN " + ps, *ids)
        res = self._db2groups(cur.fetchall())
        if (len(res) != len(userIds)
                and current.ctx.get("PartialStrategy") != "Partial"):
            retrieved = set( (g.gid for g in res) )
            for i in userIds:
                if i not in retrieved:
                    raise I.GroupNotFound("Group not found", i)
        return res

    @db.wrap("retrieving users for group")
    def getUsers(self, con, gid, current):
        cur = self._dbh.execute(con,
                "SELECT userid FROM group_entries "
                "WHERE groupid == %s",
                gid - self._go)
        res = cur.fetchall()
        if len(res) == 0:
            self._group_exists(con, gid)
            return []
        return [ x[0] + self._uo for x in res]

    @db.wrap("searching for groups")
    def search(self, con, factor, limit, current):
        phrase = (factor.replace('\\',  '\\\\')
                        .replace('%',   '\\%')
                        .replace('_',   '\\_')
                        + '%')
        cur = self._dbh.execute_limited(con, limit, 0,
                "SELECT id, name, description FROM groups "
                "WHERE name LIKE %s", phrase)
        return self._db2groups(cur.fetchall())


    @db.wrap("counting groups")
    def count(self, con, current):
        cur = self._dbh.execute(con,
                "SELECT count(name) FROM groups")
        res = cur.fetchall()
        if len(res) != 1:
            raise I.DBError(
                "Database failure while counting groups.",
                "No count fetched!")
        return long(res[0][0])


    @db.wrap("retrieving groups")
    def get(self, con, limit, offset, current):
        cur = self._dbh.execute_limited(con, limit, offset,
                "SELECT id, name, description FROM groups ")
        return self._db2groups(cur.fetchall())

    @db.wrap("setting users for group")
    def setUsers(self, con, gid, userIds, current):
        cur = self._dbh.execute(con,
                "DELETE FROM group_entries "
                "WHERE groupid == %s AND is_primary IS NULL",
                gid - self._go)
        self._addUsers(con, gid, userIds, current)

    @db.wrap("adding users to group")
    def addUsers(self, con, gid, userIds, current):
        self._addUsers(con, gid, userIds, current)

    def _addUsers(self, con, gid, userIds, current):
        self._group_exists(con, gid)
        gen = ( (gid - self._go, uid - self._uo) for uid in userIds )
        cur = self._dbh.execute_many(con,
                "INSERT INTO group_entries (userid, groupid) "
                "SELECT users.id, %s FROM users WHERE users.id == %s",
                gen)
        con.commit()

    @db.wrap("deleting users")
    def delUsers(self, con, gid, userIds, current):
        ids = tuple((i - self._uo for i in userIds))
        ps = '(' + ', '.join(('%s' for x in ids)) +')'
        cur = self._dbh.execute(con,
                "DELETE FROM group_entries "
                "WHERE groupid == %s AND is_primary IS NULL "
                "AND userid IN " + ps,
                gid - self._go, *ids)
        if cur.rowcount != len(userIds):
            self._group_exists(con, gid)
            cur = self._dbh.execute(con,
                    "SELECT userid FROM group_entries "
                    "WHERE groupid == %s AND is_primary "
                    "AND userid IN " + ps, gid, *ids)
            res = cur.fetchall()
            if len(res) > 0:
                raise I.DBError(
                        "Cannot delete users from primary group",
                        str(res))
            if current.ctx.get("PartialStrategy") != "Partial":
                #XXX: search for wrong uid and raise I.UserNotFound
                raise I.NotFound("Some users were not found")
        con.commit()

    @db.wrap("modifying group")
    def modify(self, con, group, current):
        cur = self._dbh.execute(con,
                "UPDATE groups SET "
                "name=%s, description=%s "
                "WHERE id == %s",
                group.name, group.description, group.gid - self._go)
        if cur.rowcount != 1:
            raise I.GroupNotFound("Group not found!", group.gid)
        con.commit()

    @db.wrap("creating group")
    def create(self, con, newGroup, current):
        self._dbh.execute(con,
                "INSERT INTO groups (name, description) "
                "VALUES (%s, %s)",
                newGroup.name, newGroup.description)
        cur = self._dbh.execute(con,
                "SELECT id FROM groups WHERE name=%s",
                newGroup.name)
        res = cur.fetchall()
        if len(res) != 1:
            raise I.DBError("Failed to create group",
                    "Group not found after insertion")
        con.commit()
        return res[0][0] + self._go

    @db.wrap("deleting group")
    def delete(self, con, id, current):
        gid = id - self._go
        cur = self._dbh.execute(con,
                    "SELECT userid FROM group_entries "
                    "WHERE groupid == %s AND is_primary ",
                    gid)
        res = cur.fetchall()
        if len(res) > 0:
            raise I.DBError("Cannot delete group which is primary for users",
                    str(res))
        self._dbh.execute(con,
                "DELETE FROM group_entries WHERE groupid == %s", gid)
        cur = self._dbh.execute(con,
                "DELETE FROM groups WHERE id == %s", gid)
        if cur.rowcount != 1:
            raise I.GroupNotFound("Group not found", id)
        con.commit()

    @db.wrap("adding user to multiple groups")
    def addUserToGroups(self, con, uid, groups, current):
        self._user_exists(con, uid)
        gen = ( (uid - self._uo, gid - self._go) for gid in groups )
        cur = self._dbh.execute_many(con,
                "INSERT INTO group_entries (userid, groupid) "
                "SELECT %s, groups.id FROM groups WHERE groups.id == %s",
                gen)
        con.commit()

    @db.wrap("removing user form multiple groups")
    def delUserFromGroups(self, con, uid, groups, current):
        ids = tuple((i - self._go for i in groups))
        ps = '(' + ', '.join(('%s' for x in ids)) +')'
        cur = self._dbh.execute(con,
                "DELETE FROM group_entries "
                "WHERE userid == %s AND is_primary IS NULL "
                "AND groupid IN " + ps,
                uid - self._uo, *ids)
        if cur.rowcount != len(groups):
            self._user_exists(con, uid)
            cur = self.execute(con,
                    "SELECT groupid FROM group_entries "
                    "WHERE userid == %s AND is_primary ",
                    uid)
            res = cur.fetchall()
            if len(res) > 0 and res[0] in ids:
                raise I.DBError(
                        "Cannot delete users from primary group",
                        '@' + str(res[0]))
            if current.ctx.get("PartialStrategy") != "Partial":
                #XXX: search for wrong uid and raise I.GroupNotFound
                raise I.NotFound("Some groups were not found")
        con.commit()


