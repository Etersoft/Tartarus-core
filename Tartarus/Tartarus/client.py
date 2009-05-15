import sys
import os
import Ice
import Tartarus
from Tartarus import modules

def initialize(cfgs='common', prefixes=[]):
    cfgs = _to_list(cfgs)
    props = Ice.createProperties()
    argv = sys.argv[:]
    _parse_cmd_line(props, prefixes, argv)
    cfg = props.getPropertyWithDefault('Tartarus.Config', None)

    if cfg:
        _check_load(props, cfg)
        return _init(props), argv
    if 'TARTARUS_CONFIG' in os.environ:
        _check_load(props, os.environ['TARTARUS_CONFIG'])
        return _init(props), argv
    for cfg in cfgs:
        if os.path.isabs(cfg):
            _check_load(props, cfg)
        else:
            props.load("/etc/Tartarus/Tartarus-clients.conf")
            conf_dir = props.getProperty("Tartarus.configDir")
            modules.load_config( props, conf_dir)
            #_check_load (props, "/etc/Tartarus/clients/%s.conf" % cfg)
    tmp = _init(props)
    return tmp, argv

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
        print '\033[91mError:\033[0m %s\n' % "Maybe the given workstation is not entered into the domain.."
        if not(os.path.isfile(config)):
            print "File with configuration '%s' was not found" % config
        er = ConfigError (e)
        sys.exit(1)

class ConfigError(Exception):
    def __init__(self, error):
        super(ConfigError, self).__init__(error)
        self.error = error

