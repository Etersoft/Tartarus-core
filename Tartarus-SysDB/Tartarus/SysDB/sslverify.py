
import IceSSL
from Tartarus import db, logging


_query = """
SELECT count(group_entries.id)
FROM group_entries, users
WHERE users.id == group_entries.userid
AND users.name == %s
AND group_entries.groupid IN
"""

class SimpleGroupVerifier(object):
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

    def __call__(self, info):
        try:
            return self.do_verify(info)
        except self._dbh.DBError, e:
            logging.warning(
                    "Database exception: %s: %s" %(
                        e.message, e.reason))
            return False
        except Exception:
            return False

    @db.wrap("checking permissions")
    def do_verify(self, con, info):
        princ = info.krb5Princ
        idx = princ.rfind('@')
        if idx > 0:
            princ = princ[:idx]

        cur = self._dbh.execute(con,
                self._query,
                princ, *self._groups)
        res = cur.fetchall()
        return res[0][0] > 0

    @db.wrap("getting groups indices")
    def make_groups(self, con, groups):
        ps = '(' + ', '.join( ('%s' for x in groups) ) + ')'
        cur = self._dbh.execute(con,
                "SELECT id FROM groups WHERE name IN " + ps,
                *groups)
        return [x[0] for x in cur.fetchall()]




def setup(com, dbh, vtype, props):
    if vtype.lower() != 'simple':
        raise RuntimeError('Unknown verifier type: %s' % vtype)
    gs = props.getProperty('Tartarus.SysDB.SSLVerifier.AllowGroups')
    groups = [ s for s in gs.split(':') if len(s) > 0 ]
    v = SimpleGroupVerifier(dbh, groups)
    IceSSL.setCertificateVerifier(com,v)


