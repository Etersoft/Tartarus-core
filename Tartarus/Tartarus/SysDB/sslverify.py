
import IceSSL
from Tartarus import db, logging, auth


_query = """
SELECT count(group_entries.id)
FROM group_entries, users
WHERE users.id == group_entries.userid
AND users.name == %s
AND group_entries.groupid IN
"""

class SimpleGroupVerifier(object):
    def __init__(self, verifier, groups):
        self._verifier = verifier

    def __call__(self, info):
        try:
            return self._verifier.do_verify(info)
        except self._dbh.DBError, e:
            logging.warning("Database exception: %s: %s"
                            % (e.message, e.reason))
            return False
        except Exception:
            return False

def setup(com, verifier):
    v = SimpleGroupVerifier(verifier)
    IceSSL.setCertificateVerifier(com, v)

