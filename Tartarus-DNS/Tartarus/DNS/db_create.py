
import Tartarus
from Tartarus.iface import DNS as I

import db,utils

_sqlite_db_create = [
"""
CREATE TABLE domains (
    id                INTEGER PRIMARY KEY,
    name              VARCHAR(255) NOT NULL,
    master            VARCHAR(128) DEFAULT NULL,
    last_check        INTEGER DEFAULT NULL,
    type              VARCHAR(6) NOT NULL,
    notified_serial   INTEGER DEFAULT NULL,
    account           VARCHAR(40) DEFAULT NULL
);
""",
'CREATE UNIQUE INDEX name_index ON domains(name);',
"""
CREATE TABLE records (
    id              INTEGER PRIMARY KEY,
    domain_id       INTEGER DEFAULT NULL,
    name            VARCHAR(255) DEFAULT NULL,
    type            VARCHAR(6) DEFAULT NULL,
    content         VARCHAR(255) DEFAULT NULL,
    ttl             INTEGER DEFAULT NULL,
    prio            INTEGER DEFAULT NULL,
    change_date     INTEGER DEFAULT NULL
);
""",
'CREATE INDEX rec_name_index ON records(name);',
'CREATE INDEX nametype_index ON records(name,type);',
'CREATE INDEX domain_id ON records(domain_id);',
"""
CREATE TABLE supermasters (
    ip          VARCHAR(25) NOT NULL,
    nameserver  VARCHAR(255) NOT NULL,
    account     VARCHAR(40) DEFAULT NULL
);
"""
]

_psycopg2_db_create = [
"""
CREATE TABLE domains (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    master          VARCHAR(128) DEFAULT NULL,
    last_check      INT DEFAULT NULL,
    type            VARCHAR(6) NOT NULL,
    notified_serial INT DEFAULT NULL,
    account         VARCHAR(40) DEFAULT NULL
);
""",
'CREATE UNIQUE INDEX name_index ON domains(name);',
"""
CREATE TABLE records (
    id              SERIAL PRIMARY KEY,
    domain_id       INT DEFAULT NULL,
    name            VARCHAR(255) DEFAULT NULL,
    type            VARCHAR(6) DEFAULT NULL,
    content         VARCHAR(255) DEFAULT NULL,
    ttl             INT DEFAULT NULL,
    prio            INT DEFAULT NULL,
    change_date     INT DEFAULT NULL,
    CONSTRAINT domain_exists
    FOREIGN KEY(domain_id) REFERENCES domains(id)
    ON DELETE CASCADE
);
""",
'CREATE INDEX rec_name_index ON records(name);',
'CREATE INDEX nametype_index ON records(name,type);',
'CREATE INDEX domain_id ON records(domain_id);',
"""
CREATE TABLE supermasters (
    ip VARCHAR(25) NOT NULL,
    nameserver VARCHAR(255) NOT NULL,
    account VARCHAR(40) DEFAULT NULL
);
""",
'GRANT SELECT ON supermasters TO pdns;',
'GRANT ALL ON domains TO pdns;',
'GRANT ALL ON domains_id_seq TO pdns;',
'GRANT ALL ON records TO pdns;',
'GRANT ALL ON records_id_seq TO pdns;'
]

_create_mapping = {
        'sqlite'        : _sqlite_db_create,
        'sqlite3'       : _sqlite_db_create,
        'psycopg2'      : _psycopg2_db_create
        }

def create_db():
    """Create database.

    Creates tables, indices and such stuff.
    """
    try:
        qlist = _create_mapping[db.module.__name__]
    except KeyError:
        raise I.ConfigError(
                "Database created not supported for current engine",
                db.engine)

    try:
        con = db.get_connection()
        for q in qlist:
            utils.execute(con, q)
        con.commit()
    except StandardError, e:
        raise I.DBError("Database creation failure", e.message)


def _get_sqlite_database(d):
    try:
        dbpath = db.db_opts['database']
    except KeyError:
        raise I.ConfigError('Database parameter undefined',
                            'Tartarus.DNS.db.' + e.message)
    try:
        chroot = d['chroot']
    except KeyError:
        return dbpath

    if not dbpath.startswith(chroot):
        raise I.ConfigError(
                "Database file unreachable from chroot", dbpath)

    return dbpath[len(chroot):]

def _sqlite_db_params(d):
    return [ ('launch' , 'gsqlite'),
             ('gsqlite-database', _get_sqlite_database(d)) ]

def _sqlite3_db_params(d):
    return [ ('launch' , 'gsqlite3'),
             ('gsqlite3-database', _get_sqlite_database(d)) ]

def _psycopg2_db_params(d):
    raise I.ConfigError('Database initialization unimplemented',
                        'Tartarus.DNS.db.engine')

_params_mapping = {
        'sqlite'        : _sqlite_db_params,
        'sqlite3'       : _sqlite3_db_params,
        'psycopg2'      : _psycopg2_db_params
        }

def db_pararms(d):
    d.update(_params_mapping[db.module.__name__](d))
    return d

