
import Ice
import Tartarus
from Tartarus.iface import core as C

# {{{ Default authorizer

# TODO: do we need a lock here?
_DEFAULT_AUTHORIZER = None

def set_default(obj):
    global _DEFAULT_AUTHORIZER
    old = _DEFAULT_AUTHORIZER
    _DEFAULT_AUTHORIZER = obj
    return old

def get_default():
    return _DEFAULT_AUTHORIZER

def default_authorize(marks, current):
    return _DEFAULT_AUTHORIZER(marks, current)

# }}}

# {{{ Authorizing locator

class AuthorizingLocator(Ice.ServantLocator):
    def __init__(self, authorize=default_authorize, trace=0):
        self._obj_map = {}
        self._trace = trace
        self._authorize = authorize

    def add_object(self, obj, ident):
        self._obj_map[ident] = (obj, auth_marks(obj))

    def locate(self, current):
        try:
            obj, marks = self._obj_map[current.id]
            if self._authorize(marks, current):
                return obj
        except C.PermissionError:
            raise
        except Exception, e:
            return None
        return None


    def finished(self, current, obj, cookie):
        pass

    def deactivate(self, category):
        pass

# }}}

# {{{ Marks for methods

def mark(*marks):
    def wrapper(method):
        method.tart_authorize_marks = marks
        return method
    return wrapper

def auth_marks(obj):
    res = {}
    for x in dir(obj):
        if not (x.startswith('_') or x.startswith('ice_')):
            try:
                res[x] = getattr(obj, x).tart_authorize_marks
            except AttributeError:
                pass
    return res

# }}}

