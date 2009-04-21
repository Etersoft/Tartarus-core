from enum import Enum
import Tartarus
from Tartarus.iface import core as C

def _checked_configure(svc_proxy, force, params = None):
    if not params:
        params = {}
    if not svc_proxy:
        raise C.RuntimeError('Proxy not found')

    svc = C.ServicePrx.checkedCast(svc_proxy)
    if not svc:
        raise C.RuntimeError('Wrong service proxy')

    if svc.isConfigured() and not force:
        raise C.RuntimeError('Database already exists')
    params['force'] = force
    svc.configure(params)

class Failure(RuntimeError): pass

from Tartarus.system import consdialog
import sys

def _cdialog_mc(name, bases, dict):
    for i in 'yesno ask password choice force'.split():
        method = getattr(consdialog, i)
        dict[i] = staticmethod(method)
        #dict['x'+i] = _cdwraper(method)
    return type(name, bases, dict)

def _cdwraper(function):
    def wrapper(self, var, *args, **kwargs):
        self.opts[var] = function(*args, **kwargs)
    return wrapper

class ConsDialog:
    __metaclass__ = _cdialog_mc
    def __init__(self, questions):
        pass
    @staticmethod
    def info(msg):
        print 'INFO: ' + msg
    @staticmethod
    def warning(msg):
        print 'WARNING: ' + msg
    @staticmethod
    def error(msg):
        print 'ERROR: ' + msg

class TopologicalSorter:
    def __init__(self, names, deps):
        self.__names = names
        self.__deps = deps
        self.__colors = dict(((name, 0) for name in names))
        self.__result = []
    def __push(self, name):
        if self.__colors[name] is 1:
            raise RuntimeError('Cycle detected for "%s"' % name)
        if self.__colors[name] is 2:
            return
        self.__colors[name] = 1
        for dep in self.__deps[name]:
            self.__push(dep)
        self.__colors[name] = 2
        self.__result.append(name)
    def do(self, debug=False):
        if debug:
            print 'Names:', self.__names
            print 'Deps:', self.__deps
        for name in self.__names:
            self.__push(name)
        if debug:
            print 'Result:', self.__result
        return self.__result

class Wizard:
    __features_map = {}
    __methods = {}
    def __init__(self, dialog=ConsDialog, debug=False):
        self.dialog = dialog(self)
        self.__debug = debug
        self.__disabled = set()
        self.features = None
    @staticmethod
    def feature(name):
        def registrator(method):
            mname = method.__name__
            if mname in Wizard.__methods:
                raise RuntimeError('Method "%s" allready registered')
            Wizard.__methods[mname] = method
            if name not in Wizard.__features_map:
                Wizard.__features_map[name] = [mname]
            else:
                Wizard.__features_map[name].append(mname)
            return method
        return registrator
    def disable(self, name):
        self.__disabled.add(name)
    def enable(self, name):
        self.__disabled.discard(name)
    def run(self, *features):
        self.features = features
        names = self.__calcNames(features)
        deps = self.__calcDepGraph(names)
        for name in self.__tSort(names, deps):
            if name in self.__disabled: continue
            if self.__debug:
                print '\033[92m*\033[0m Running: ' + name
            ret = self.__methods[name](self)
            if ret is not None: self.fail(str(ret))
        self.features = None
    @staticmethod
    def fail(msg):
        raise Failure(msg)
    @staticmethod
    def __tSort(names, deps):
        return TopologicalSorter(names, deps).do()
    @staticmethod
    def __calcDepGraph(names):
        deps = dict(((name, []) for name in names))
        for name in names:
            method = Wizard.__methods[name]
            for dep in getattr(method, '_run_after', []):
                if dep in names: deps[name].append(dep)
            for dep in getattr(method, '_run_before', []):
                if dep in names: deps[dep].append(name)
        return deps
    @staticmethod
    def __calcNames(features):
        fmap = Wizard.__features_map
        names = []
        if '*' in fmap:
            flist = ['*']
            flist.extend(features)
        else:
            flist = features
        for f in flist:
            if f not in fmap:
                sys.stderr.write('Warning: feature %s is not registered\n' % f)
                continue
            for name in fmap[f]:
                names.append(name)
        return names
    def __str__(self):
        ret = ['Answers:']
        for i in self.__dialog.answers.iteritems():
            ret.append('  %s: %s' % i)
        return '\n'.join(ret)

feature = Wizard.feature

def after(*names):
    def modificator(method):
        l = getattr(method, '_run_after', [])
        l.extend(names)
        method._run_after = l
        return method
    return modificator

def before(*names):
    def modificator(method):
        l = getattr(method, '_run_before', [])
        l.extend(names)
        method._run_before = l
        return method
    return modificator

