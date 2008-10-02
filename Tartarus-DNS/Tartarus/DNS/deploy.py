
import Tartarus

import utils, cfgfile
from Tartarus.iface import core as ICore
from Tartarus import db

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

def create_db(dbh):
    """Create database.

    Creates tables, indices and such stuff.
    """
    try:
        qlist = _create_mapping[dbh.modname]
    except KeyError:
        raise dbh.ConfigError(
                "Database created not supported for current engine",
                dbh.engine)

    try:
        con = dbh.get_connection()
        for q in qlist:
            dbh.execute(con, q)
        con.commit()
    except StandardError, e:
        raise dbh.DBError("Database creation failure", e.message)


def _get_sqlite_database(d, dbh):
    try:
        dbpath = dbh.options['database']
    except KeyError:
        raise dbh.ConfigError('Database parameter undefined',
                            'Tartarus.DNS.db.' + e.message)
    try:
        chroot = d['chroot']
    except KeyError:
        return dbpath

    if not dbpath.startswith(chroot):
        raise dbh.ConfigError(
                "Database file unreachable from chroot", dbpath)

    return dbpath[len(chroot):]

def _sqlite_db_params(d, dbh):
    return [ ('launch' , 'gsqlite'),
             ('gsqlite-database', _get_sqlite_database(d, dbh)) ]

def _sqlite3_db_params(d, dbh):
    return [ ('launch' , 'gsqlite3'),
             ('gsqlite3-database', _get_sqlite_database(d, dbh)) ]

def _psycopg2_db_params(d, dbh):
    raise dbh.ConfigError('Database initialization unimplemented',
                        'Tartarus.DNS.db.engine')

_params_mapping = {
        'sqlite'        : _sqlite_db_params,
        'sqlite3'       : _sqlite3_db_params,
        'psycopg2'      : _psycopg2_db_params
        }

def db_pararms(d, dbh):
    try:
        d.update(_params_mapping[dbh.modname](d, dbh))
        return d
    except KeyError:
        raise dbh.ConfigError('Database engine not supported', dbn.engine)


class DNSService(ICore.Service):
    def __init__(self, dbh, config_file, enabe_deploy):
        self._dbh = dbh
        self._cfg_file = config_file


    def do_deploy(self):
        opt_dict = dict(cfgfile.parse(self._cfg_file))
        db_pararms(opt_dict, self._dbh)
        try:
            cfgfile.gen(self._cfg_file, opt_dict.iteritems())
        except IOError:
            raise self.dbh_.ConfigError("Failed to alter configuration file",
                                 self._cfg_file)
        create_db(self._dbh)


    @db.wrap("checking configuration")
    def isConfigured(self, con, current):
        #a bit heuristic...
        try:
            self._dbh.execute(con,
                    "SELECT count(*) FROM records")
            self._dbh.execute(con,
                    "SELECT count(*) FROM domains")
            return True
        except:
            pass
        return False

    def configure(self, opts, current):
        if 'force' in opts:
            self._dbh.remove()
        self.do_deploy()

    def getName(self, current):
        return "DNS"


