
import IceSSL
import Tartarus
from Tartarus import db, logging
from Tartarus.iface import core as C


_query = """
SELECT count(group_entries.id)
FROM group_entries, users
WHERE users.id == group_entries.userid
AND users.name == %s
AND group_entries.groupid IN
"""


class SimpleGroupAuthorizer(object):
    def __init__(self, dbh, groups):
        self._dbh = dbh
        self._groups = self.make_groups(groups)
        if len(groups) != len(self._groups):
            logging.warning(
                    "%s of %s groups not found in database "
                    "and will be ignored by ssl verifier" %
                    (len(groups) - len(self._groups), len(groups)) )
        ps = '(' + ', '.join( ('%s' for x in self._groups) ) + ')'
        self._query = _query + ps

    def __call__(self, marks, current):
        try:
            return self.do_auth(marks, current)
        except self._dbh.DBError, e:
            logging.warning("Database exception: %s: %s"
                            % (e.message, e.reason) )
            return False

    def do_auth(self, marks, current):
        m = marks.get(current.operation)
        if not m:
            return True
        if 'write' not in m and 'admin' not in m:
            return True
        try:
            info = IceSSL.getConnectionInfo(current.con)
        except TypeError, e:
            # this is not SSL with Kerberos; so we don't care
            return True

        if 'host' in m and info.krb5Princ.startswith('host/'):
            return True

        return self.do_verify(current.operation, info)


    @db.wrap("checking permissions")
    def do_verify(self, con, operation, info):
        princ = info.krb5Princ
        idx = princ.rfind('@')
        if idx > 0:
            princ = princ[:idx]

        cur = self._dbh.execute(con, self._query,
                                princ, *self._groups)
        res = cur.fetchall()
        if res[0][0] > 0:
            return True
        raise C.PermissionError("Permission denied", operation, princ)



    @db.wrap("getting groups indices")
    def make_groups(self, con, groups):
        ps = '(' + ', '.join( ('%s' for x in groups) ) + ')'
        cur = self._dbh.execute(con,
                "SELECT id FROM groups WHERE name IN " + ps,
                *groups)
        return [x[0] for x in cur.fetchall()]


