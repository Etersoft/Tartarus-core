
from Tartarus import logging, db
from Tartarus.iface import core as ICore

_create_sqlite3 = [
"""
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR UNIQUE NOT NULL,
    fullname    VARCHAR DEFAULT NULL,
    shell       VARCHAR DEFAULT "/bin/bash"
);
""",
"""
CREATE TABLE groups (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR UNIQUE NOT NULL,
    description VARCHAR DEFAULT NULL
);
""",
"""
CREATE TABLE group_entries (
    id          INTEGER PRIMARY KEY,
    userid      INTEGER NOT NULL,
    groupid     INTEGER NOT NULL,
    is_primary  BOOLEAN DEFAULT NULL,
    UNIQUE (userid, groupid),
    UNIQUE (userid, is_primary)
);
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



