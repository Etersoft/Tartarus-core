
import IceSSL
from Tartarus import logging, auth


class SimpleGroupVerifier(object):
    def __init__(self, verifier, groups):
        self._verifier = verifier

    def __call__(self, info):
        try:
            return self._verifier.do_verify(info)
        except Exception:
            return False

def setup(com, verifier):
    v = SimpleGroupVerifier(verifier)
    IceSSL.setCertificateVerifier(com, v)

