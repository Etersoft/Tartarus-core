
import Tartarus, os
from Tartarus import logging
import Tartarus.iface.DNS as I

import db, db_create, utils, cfgfile

class ServerI(I.Server):
    def __init__(self, cfg_file_name):
        I.Server.__init__(self)
        dir, name = os.path.split(cfg_file_name)
        if len(name) < 1 or not os.path.isdir(dir):
            raise I.ConfigError("Bad config file specified", cfg_file_name)
        self._config_file = cfg_file_name

    def getZones(self, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con, 'SELECT id FROM domains')
            result = [ utils.proxy(I.ZonePrx, current, "DNS-Zone", str(x[0]))
                       for x in cur.fetchall() ];
            return result
        except db.module.Error, e:
            raise I.DBError("Database failure", e.message)

    def getZone(self, name, current):
        try:
            con = db.get_connection()
            cur = utils.execute(con,
                    'SELECT id FROM domains WHERE name=%s',name)
            result = cur.fetchall()
            if len(result) != 1:
                raise I.ObjectNotFound("Could not locate zone in the database")
            return utils.proxy(I.ZonePrx, current, "DNS-Zone", str(result[0][0]))
        except db.module.Error, e:
            raise I.DBError("Database failure", e.message)

    def createZone(self, name, soar, current):
        try:
            con = db.get_connection()
            utils.execute(con,
                    'INSERT INTO domains (name, type) VALUES (%s, %s)',
                    name, 'NATIVE')
            con.commit()
        except db.module.Error, e:
            raise I.DBError("Zone creation failed", e.message)

    def _dropZone(self, con, id):
        try:
            cur = utils.execute(con,
                    "DELETE FROM domains WHERE id=%s", id)
            if cur.rowcount != 1:
                raise I.ObjectNotFound("Zone not found in database.")
            utils.execute(con,
                    "DELETE FROM records WHERE domain_id=%s", id)
            con.commit()
        except db.module.Error, e:
            raise I.DBError("Zone delition failed", e.message)

    def deleteZone(self, name, current):
        con = db.get_connection()
        id = None
        try:
            cur = utils.execute(con,
                    "SELECT id FROM domains WHERE name=%s", name)
            res = cur.fetchall()
            if len(res) != 1:
                raise I.ObjectNotFound("No such zone.")
            id = res[0][0]
        except db.module.Error, e:
            raise I.DBError("Database failure.", e.message)
        self._dropZone(con, id)

    def deleteZoneByRef(self, proxy, current):
        id = utils.name(current, proxy.ice_getIdentity())
        self._dropZone(db.get_connection(), id)

    _supported_options = set((
        "allow-recursion",
        "recursor"
        ))

    def getOptions(self, current):
        try:
            return [ I.ServerOption(*pair)
                     for pair in cfgfile.parse(self._config_file)
                     if pair[0] in self._supported_options]

        except IOError:
            raise I.ConfigError("Failed to read configuration file",
                                 self._config_file)

    def _convert_option(self, opt):
        if opt.name not in self._supported_options:
            raise I.ValueError("Unsupported option", opt.name)
        return opt.name, opt.value

    def _reload_config(self):
        try:
            retval = os.system("pdns_control cycle &>/dev/null")
            if os.WIFEXITED(retval) and os.WEXITSTATUS(retval) == 0:
                return
        except:
            pass
        raise I.Error('Failed to reload configuration file. '
                      'All changes will be applied on next server restart.')

    def setOptions(self, opts, current):
        try:
            if len(opts) < 1:
                return
            new_opts = [ self._convert_option(opt) for opt in opts ]
            # save all extra options
            old_opts = [ pair
                         for pair in cfgfile.parse(self._config_file)
                         if pair[0] not in self._supported_options ]
            new_opts += old_opts
            cfgfile.gen(self._config_file, new_opts)
        except IOError:
            raise I.ConfigError("Failed to alter configuration file",
                                 self._config_file)
        self._reload_config()


    def changeOptions(self, opts, current):
        try:
            if len(opts) < 1:
                return
            opts_dict = dict( (self._convert_option(opt)
                               for opt in opts) )
            new_opts = [ pair
                         for pair in cfgfile.parse(self._config_file)
                         if pair[0] not in opts_dict ]
            new_opts.extend(opts_dict.iteritems())
            cfgfile.gen(self._config_file, new_opts)
        except IOError:
            raise I.ConfigError("Failed to alter configuration file",
                                 self._config_file)
        self._reload_config()



    def setOption(self, opt, current):
        raise I.ValueError("Unsupported option", opt.name)

    def initNewDatabaseUnsafe(self, opts, current):
        if len(opts) > 0:
            try:
               cfgfile.gen( ((opt.name, opt.value)
                             for opt in opts),
                           self._config_file)
            except IOError:
                raise I.ConfigError("Failed to alter configuration file",
                                     self._config_file)
        db_create.create_db()
        self._reload_config()

