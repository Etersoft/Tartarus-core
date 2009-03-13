
import Ice
import Tartarus
from Tartarus import logging
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
    if _DEFAULT_AUTHORIZER:
        return _DEFAULT_AUTHORIZER(marks, current)
    return True

# }}}

# {{{ Authorizing locators

class DefaultSrvLocator(Ice.ServantLocator):
    def __init__(self, obj, marks=None,
                 authorize=default_authorize):
        self._obj = obj
        self._marks = marks or {}
        self._authorize = authorize

    def locate(self, current):
        try:
            if self._authorize(self._marks, current):
                return self._obj
        except C.PermissionError:
            raise
        except Exception, e:
            c = current.adapter.getCommunicator()
            logging.warning("Refusing permission because of exception. "
                            "Object: %s. Operation: %s. Exception %s: %s."
                            % (c.identityToString(current.id),
                               current.operation,
                               type(e).__name__, e))
            return None
        return None

    def finished(self, current, obj, cookie):
        pass
    def deactivate(self, category):
        pass


class SrvLocator(Ice.ServantLocator):
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
        except Ice.ObjectNotExistException:
            return None
        except C.PermissionError:
            raise
        except Exception, e:
            c = current.adapter.getCommunicator()
            logging.warning("Refusing permission because of exception. "
                            "Object: %s. Operation: %s. Exception %s: %s."
                            % (c.identityToString(current.id),
                               current.operation,
                               type(e).__name__, e))
            return None
        return None

    def finished(self, current, obj, cookie):
        pass

    def deactivate(self, category):
        pass

class DecoratingLocator(Ice.ServantLocator):
    def __init__(self, locator, authorize=default_authorize, trace=0):
        self._trace = trace
        self._authorize = authorize
        self.__locator = locator

    def locate(self, current):
        try:
            obj = self.__locator.locate(current)
            marks = getattr(obj, 'marks', None) or auth_marks(obj)
            if self._authorize(marks, current):
                return obj
        except Ice.ObjectNotExistException:
            return None
        except C.PermissionError:
            raise
        except Exception, e:
            c = current.adapter.getCommunicator()
            logging.warning("Refusing permission because of exception. "
                            "Object: %s. Operation: %s. Exception %s: %s."
                            % (c.identityToString(current.id),
                               current.operation,
                               type(e).__name__, e))
            return None
        return None

    def __getattr__(self, *args):
        return getattr(self.__locator, *args)

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

