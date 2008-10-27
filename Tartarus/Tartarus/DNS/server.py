

import Tartarus, os, IceSSL, socket
from Tartarus import logging, db
import Tartarus.iface.DNS as I
import Tartarus.iface.core as ICore

import utils, cfgfile


class ServerI(I.Server):
    def __init__(self, cfg_file_name, dbh, do_reload=True):
        self._dbh = dbh
        self._do_reload = do_reload
        I.Server.__init__(self)
        path, name = os.path.split(cfg_file_name)
        if len(name) < 1 or not os.path.isdir(path):
            raise ICore.ConfigError("Bad config file specified", cfg_file_name)
        self._config_file = cfg_file_name
        # enshure server is here and works with actual config file
        self._reload_config()

    @db.wrap("retrieving all zones")
    def getZones(self, con, current):
        cur = self._dbh.execute(con, 'SELECT id FROM domains')
        result = [ utils.proxy(I.ZonePrx, current, "DNS-Zone", str(x[0]))
                   for x in cur.fetchall() ]
        return result

    @db.wrap("retrieving zone by name")
    def getZone(self, con, name, current):
        cur = self._dbh.execute(con,
                'SELECT id FROM domains WHERE name=%s',name)
        result = cur.fetchall()
        if len(result) != 1:
            raise ICore.NotFoundError("Could not locate zone in the database")
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
            raise ICore.DBError("Zone creation failed"
                    "Could not locate zone in the database")
        n = str(result[0][0])
        cur = self._dbh.execute(con,
                "INSERT INTO records (domain_id, name, type, content)"
                "VALUES (%s, %s, 'SOA', %s)",
                n, name, utils.soar2str(soar))
        if  cur.rowcount != 1:
            raise ICore.DBError("Zone creation failed",
                    "Failed to add SOA Record.")
        con.commit()
        return utils.proxy(I.ZonePrx, current, "DNS-Zone", n)


    def _dropZone(self, con, key):
        cur = self._dbh.execute(con,
                "DELETE FROM domains WHERE id=%s", key)
        if cur.rowcount != 1:
            raise ICore.NotFoundError("Zone not found in database.")
        self._dbh.execute(con,
                "DELETE FROM records WHERE domain_id=%s", key)
        con.commit()

    @db.wrap("Deleting a zone")
    def deleteZone(self, con, name, current):
        cur = self._dbh.execute(con,
                "SELECT id FROM domains WHERE name=%s", name)
        res = cur.fetchall()
        if len(res) != 1:
            raise ICore.NotFoundError("No such zone.")
        key = res[0][0]
        self._dropZone(con, key)

    @db.wrap("Deleting a zone")
    def deleteZoneByRef(self, con, proxy, current):
        key = utils.name(current, proxy.ice_getIdentity())
        self._dropZone(con, key)


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
            raise ICore.ConfigError("Failed to read configuration file",
                                 self._config_file)

    def _convert_option(self, opt):
        if opt.name not in self._supported_options:
            raise ICore.ValueError("Unsupported option", opt.name)
        return opt.name, opt.value

    def _reload_config(self):
        if not self._do_reload:
            return
        try:
            retval = os.system("pdns_control cycle &>/dev/null")
            if os.WIFEXITED(retval) and os.WEXITSTATUS(retval) == 0:
                return
        except Exception:
            pass
        raise ICore.RuntimeError('Failed to reload configuration file. '
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
            raise ICore.ConfigError("Failed to alter configuration file",
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
            raise ICore.ConfigError("Failed to alter configuration file",
                                 self._config_file)
        self._reload_config()


    def _rev_zone_name(self, con, addr):
        v = addr.split('.')
        if len(v) != 4:
            raise ICore.ValueError('Wrong address', addr)
        z1 = v[0] + '.in-addr.arpa'
        z2 = v[1] + '.' + z1
        z3 = v[2] + '.' + z2
        cur = self._dbh.execute(con,
                "SELECT name FROM domains "
                "WHERE name IN (%s, %s, %s) "
                "ORDER BY length(name) LIMIT 1",
                z1,z2,z3)
        res = cur.fetchall()
        if len(res) != 1:
            raise utils.NoSuchObject
        return res[0][0]


    def _set_machine(self, con, hostname, addr, rzone):
        query = ("INSERT OR REPLACE INTO records "
                 "(domain_id, name, type, content)"
                 "SELECT id, %s, %s, %s FROM domains "
                 "WHERE name == %s ")
        idx = hostname.find('.')
        if idx < 0:
            raise ValueError('Wrong hostname: ' , hostname)
        domainname = hostname[idx+1:]

        cur = self._dbh.execute(con, query,
                hostname, 'A', addr, domainname)
        if cur.rowcount != 1:
            raise ICore.ValueError('Zone update failure', hostname)

        cur2 = self._dbh.execute(con, query,
                utils.rev_zone_entry(addr), 'PTR', hostname, rzone)
        if cur2.rowcount != 1:
            raise ICore.ValueError('Reverse zone update failure', addr)
        con.commit()

    @db.wrap("updating host information")
    def updateHost(self, con, hostname, addr, current):
        props = current.adapter.getCommunicator().getProperties()
        rzone = props.getProperty('Tartarus.DNS.reverseZones')
        if len(rzone) == 0:
            rzone = self._rev_zone_name(con, addr)
        self._set_machine(con, hostname, addr, rzone)



    @db.wrap("updating information for a host")
    def updateThisHost(self, con, current):
        try:
            info = IceSSL.getConnectionInfo(current.con)
        except TypeError:
            raise ICore.PermissionError("Permission denied",
                    "<non-krb connection>", 'updateHost')
        if not info.krb5Princ.startswith('host/'):
            raise ICore.PermissionError("Permission denied",
                    info.krb5Princ, 'updateHost')
        # krb5princ = 'host/f.q.d.n@REALM.NAME
        # we remove host/ part
        hostname = info.krb5Princ[5:]
        # and then @REALM.NAME part, if any
        idx = hostname.rfind('@')
        if idx > 0:
            hostname = hostname[:idx]

        addr = info.remoteAddr

        # simple check that it is ipv4:
        try:
            socket.inet_aton(addr)
        except socket.error:
            raise ICore.ValueError('Could not get IP address', addr)

        props = current.adapter.getCommunicator().getProperties()
        rzone = props.getProperty('Tartarus.DNS.reverseZone')
        if len(rzone) == 0:
            rzone = self._rev_zone_name(con, addr)
        self._set_machine(con, hostname, addr, rzone)








