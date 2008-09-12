
import IceSSL
from Tartarus import db, logging

class SimpleGroupVerifier(object):
    def __init__(self, dbh, group):
        self._dbh = dbh
        self._group = group

    def __call__(self, info):
        try:
            return self.do_verify(info)
        except self._dbh.DBError, e:
            logging.trace("Verifier",
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

        print princ

        cur = self._dbh.execute(con,
                "SELECT groups.name "
                "FROM groups, group_entries, users "
                "WHERE groups.id == group_entries.groupid "
                "AND group_entries.userid == users.id "
                "AND users.name == %s",
                princ)
        res = cur.fetchall()
        result = set( (str(x[0]) for x in res) )
        print self._group, result
        return self._group in result


def setup(com, dbh, group):
    v = SimpleGroupVerifier(dbh, group)
    IceSSL.setCertificateVerifier(com,v)


