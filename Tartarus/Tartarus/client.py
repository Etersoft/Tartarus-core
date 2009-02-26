import sys
import os
import Ice
import Tartarus

def initialize(cfgs='common', prefixes=[]):
    cfgs = _to_list(cfgs)
    props = Ice.createProperties()
    argv = sys.argv[:]
    _parse_cmd_line(props, prefixes, argv)
    cfg = props.getPropertyWithDefault('Tartarus.Config', None)
    if cfg:
        props.load(cfg)
        return _init(props), argv
    if 'TARTARUS_CONFIG' in os.environ:
        props.load(os.environ['TARTARUS_CONFIG'])
        return _init(props), argv
    for cfg in cfgs:
        if os.path.isabs(cfg):
            props.load(cfg)
        else:
            props.load('/etc/Tartarus/clients/%s.config' % cfg)
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

