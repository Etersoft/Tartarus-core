
from Tartarus import logging

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

def create_db(dbh):
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

