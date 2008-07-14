
import Tartarus, os
from Tartarus import logging, db
import Tartarus.iface.DNS as I

import deploy, utils, cfgfile

class ServerI(I.Server):
    def __init__(self, cfg_file_name, dbh, do_reload=True):
        self._dbh = dbh
        self._do_reload = do_reload
        I.Server.__init__(self)
        dir, name = os.path.split(cfg_file_name)
        if len(name) < 1 or not os.path.isdir(dir):
            raise I.ConfigError("Bad config file specified", cfg_file_name)
        self._config_file = cfg_file_name
        # enshure server is here and works with actual config file
        self._reload_config()

    @db.wrap("retrieving all zones")
    def getZones(self, con, current):
        cur = self._dbh.execute(con, 'SELECT id FROM domains')
        result = [ utils.proxy(I.ZonePrx, current, "DNS-Zone", str(x[0]))
                   for x in cur.fetchall() ];
        return result

    @db.wrap("retrieving zone by name")
    def getZone(self, con, name, current):
        cur = self._dbh.execute(con,
                'SELECT id FROM domains WHERE name=%s',name)
        result = cur.fetchall()
        if len(result) != 1:
            raise I.ObjectNotFound("Could not locate zone in the database")
        return utils.proxy(I.ZonePrx, current, "DNS-Zone", str(result[0][0]))

    @db.wrap("creating a zone")
    def createZone(self, con, name, soar, current):
        self._dbh.execute(con,
                'INSERT INTO domains (name, type) VALUES (%s, %s)',
                name, 'NATIVE')
        # we'll need id later to create proxy
        cur = self._dbh.execute(con,
                'SELECT id FROM domains WHERE name=%s',name)
        result = cur.fetchall()
        if len(result) != 1:
            raise I.DBError("Zone creation failed"
                    "Could not locate zone in the database")
        id = str(result[0][0])
        cur = self._dbh.execute(con,
                "INSERT INTO records (domain_id, name, type, content)"
                "VALUES (%s, %s, 'SOA', %s)",
                id, name, utils.soar2str(soar))
        if  cur.rowcount != 1:
            raise I.DBError("Zone creation failed",
                    "Failed to add SOA Record.")
        con.commit()
        return utils.proxy(I.ZonePrx, current, "DNS-Zone", id)


    def _dropZone(self, con, id):
        cur = self._dbh.execute(con,
                "DELETE FROM domains WHERE id=%s", id)
        if cur.rowcount != 1:
            raise I.ObjectNotFound("Zone not found in database.")
        self._dbh.execute(con,
                "DELETE FROM records WHERE domain_id=%s", id)
        con.commit()

    @db.wrap("Deleting a zone")
    def deleteZone(self, con, name, current):
        id = None
        cur = self._dbh.execute(con,
                "SELECT id FROM domains WHERE name=%s", name)
        res = cur.fetchall()
        if len(res) != 1:
            raise I.ObjectNotFound("No such zone.")
        id = res[0][0]
        self._dropZone(con, id)

    @db.wrap("Deleting a zone")
    def deleteZoneByRef(self, con, proxy, current):
        id = utils.name(current, proxy.ice_getIdentity())
        self._dropZone(con, id)


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
        if not self._do_reload:
            return
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


