
from Tartarus import logging, db
from Tartarus.iface import core as ICore

_create_sqlite3 = [
"""
CREATE TABLE groups (
    gid INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR DEFAULT "" NOT NULL ON CONFLICT REPLACE
);
""",
"""
CREATE TABLE users (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    gid INTEGER NOT NULL,
    name VARCHAR UNIQUE NOT NULL,
    fullname VARCHAR DEFAULT "" NOT NULL ON CONFLICT REPLACE,
    shell VARCHAR DEFAULT "/bin/bash"
        NOT NULL ON CONFLICT REPLACE
);
""",
"""
CREATE TABLE real_group_entries (
    uid INTEGER NOT NULL,
    gid INTEGER NOT NULL,
    UNIQUE (uid, gid)
);
""",
"""
CREATE VIEW group_entries AS
    SELECT uid, gid, 1 AS is_primary FROM users
    UNION ALL
    SELECT uid, gid, 0 AS is_primary FROM real_group_entries;
""",
"""
CREATE TRIGGER on_user_add
BEFORE INSERT ON users
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, "You can't add user to non-existant group")
        WHERE (SELECT gid FROM groups WHERE gid = NEW.gid) IS NULL;
END;
""",
"""
CREATE TRIGGER on_user_change
BEFORE UPDATE ON users
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, "You can't add user to non-existant group")
        WHERE (SELECT gid FROM groups WHERE gid = NEW.gid) IS NULL;
    DELETE FROM real_group_entries
        WHERE real_group_entries.gid == NEW.gid;
END;
""",
"""
CREATE TRIGGER on_user_deletion
BEFORE DELETE ON users
FOR EACH ROW BEGIN
    DELETE FROM real_group_entries WHERE real_group_entries.uid == OLD.uid;
END;
""",
"""
CREATE TRIGGER on_group_deletion
BEFORE DELETE ON groups
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, "You can't delete group which is primary for some users")
        FROM users WHERE users.gid == OLD.gid;
    DELETE FROM real_group_entries WHERE real_group_entries.gid == OLD.gid;
END;
""",
"""
CREATE TRIGGER on_adding_user_to_group
BEFORE INSERT ON real_group_entries
FOR EACH ROW BEGIN
    SELECT RAISE(ABORT, "You can't add non-existant user to group")
        WHERE (SELECT uid FROM users WHERE uid = NEW.uid) IS NULL;
    SELECT RAISE(ABORT, "You can't add user to non-existant group")
        WHERE (SELECT gid FROM groups WHERE gid = NEW.gid) IS NULL;
    SELECT RAISE(ABORT, "You can't add a user to the group more than once")
        FROM group_entries
        WHERE group_entries.uid == NEW.uid AND group_entries.gid == NEW.gid;
END;
"""
]

_creator_map = {
        'sqlite3' : _create_sqlite3
        }

class SysDBService(ICore.Service):
    def __init__(self, dbh, enable_deploy):
        self._dbh = dbh
        self.enable_deploy = enable_deploy

    def getName(self, current):
        return 'SysDB'

    def create_db(self):
        dbh = self._dbh
        logging.trace(__name__, 'Initializing empty database', dbh.trace)
        try:
            create = _creator_map[dbh.modname]
        except KeyError:
            raise dbh.ConfigError('Database engine not supported', dbh.engine)

        try:
            con = dbh.get_connection()
            for q in create:
                dbh.execute(con, q)
            con.commit()
        except dbh.Error, e:
            raise dbh.DBError(
                    'Database failure while initializing new database',
                    e.message)


    @db.wrap("checking configuration")
    def isConfigured(self, con, current):
        try:
            self._dbh.execute(con, "SELECT count(*) FROM users")
            self._dbh.execute(con, "SELECT count(*) FROM groups")
            self._dbh.execute(con, "SELECT count(*) FROM group_entries")
            return True
        except Exception:
            return False

    def configure(self, opts, current):
        if not self.enable_deploy:
            raise ICore.RunimeError("Deployment was disabled")
        if 'force' in opts:
            self._dbh.remove()
        self.create_db()



