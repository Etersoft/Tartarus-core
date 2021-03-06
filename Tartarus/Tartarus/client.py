import sys
import os
import Ice
import Tartarus
from Tartarus.iface import DNS
from Tartarus.iface import Time

_TimeServerPrx_ = "Tartarus.Time.ServerPrx"
_SysDBUserPrx_ = "Tartarus.SysDB.UserManagerPrx"
_SysDBGroupPrx_ = "Tartarus.SysDB.GroupManagerPrx"
_KerberosKadminPrx_ = "Tartarus.Kerberos.KadminPrx"
_DNSServerPrx_ = "Tartarus.DNS.ServerPrx"

_PrxList_ = [_TimeServerPrx_, _SysDBUserPrx_, _SysDBGroupPrx_, _KerberosKadminPrx_, _DNSServerPrx_]

def initialize(cfgs='common', prefixes=[], domain = None):
    cfgs = _to_list(cfgs)
    props = Ice.createProperties()
    argv = sys.argv[:]
    _parse_cmd_line(props, prefixes, argv)
    cfg = props.getPropertyWithDefault('Tartarus.Config', None)

    if cfg:
        _check_load(props, cfg)
    elif 'TARTARUS_CONFIG' in os.environ:
        _check_load(props, os.environ['TARTARUS_CONFIG'])
    else:
        try:
            _check_load(props, "/etc/Tartarus/Tartarus-clients.conf")
        except:
            pass

    conf_dir = props.getProperty("Tartarus.configDir")
    if not conf_dir:
        conf_dir = "/etc/Tartarus/clients"

    for cfg in cfgs:
        if os.path.isabs(cfg):
            _check_load(props, cfg)
        else:
            _check_load(props, "%s/%s.conf" % (conf_dir, cfg))

    if domain == None:
        domain = props.getProperty("Tartarus.Domain")
    _check_props(props, domain)
    return _init(props), argv

def _parse_cmd_line(props, prefixes, argv):
    props.parseIceCommandLineOptions(argv)
    prefixes = _to_list(prefixes) + ['Tartarus']
    for i in prefixes:
        props.parseCommandLineOptions(i, argv)

def _init(props):
    def _prefixed(name):
        return props.getPropertiesForPrefix(name).itervalues()
    Tartarus.slices.trace = props.getPropertyAsInt("Tartarus.import.Trace")
    Tartarus.slices.path += _prefixed('Tartarus.addSlicePath.')
    idata = Ice.InitializationData()
    idata.properties = props
    return Ice.initialize(idata)

def _to_list(vals):
    if isinstance(vals, str):
        return vals.split()
    return vals

def _check_load(ice_props, config):
    try:
        ice_props.load(config)
    except Exception, e:
        print "Maybe the given workstation is not entered into the domain.."
        if not(os.path.isfile(config)):
            print "File with configuration '%s' was not found" % config
        er = ConfigError (e)
        sys.exit(1)

def _check_props(ice_props, hostname):
    for key, value in ice_props.getPropertiesForPrefix("").iteritems():
        if (key in _PrxList_) and ('-h' not in value.split()):
            if  hostname == None:
                raise ConfigError ("Hostname for %s was not set." % key)
            value += " -h %s" % hostname
            ice_props.setProperty(key, value)

    return ice_props

def getTimePrx(comm):
    prx = comm.propertyToProxy(_TimeServerPrx_)
    t = Time.ServerPrx.checkedCast(prx)
    return t

def getDNSPrx(comm):
    prx = comm.propertyToProxy(_DNSServerPrx_)
    t = DNS.ServerPrx.checkedCast(prx)
    return t

class ConfigError(Exception):
    def __init__(self, error):
        super(ConfigError, self).__init__(error)
        self.error = error

