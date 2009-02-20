class _Options:
    def __init__(self, props):
        p = props.getPropertyWithDefault
        for attr, oname, default in self.__opts:
            setattr(self, attr, p(oname, default))
    @classmethod
    def init(cls, props):
        if cls.__instance: raise RuntimeError('You should not init options again')
        cls.__instance = cls(props)
    @classmethod
    def get(cls):
        if not cls.__instance: raise RuntimeError('Options do not initialized')
        return cls.__instance
    @classmethod
    def _defOpt(cls, attr, oname, default):
        cls.__opts.append((attr, oname, default))
    __opts = []
    __instance = None

# define options
o = _Options._defOpt
o('cfg_fname', 'Tartarus.DHCP.ConfigFile', '/usr/share/Tartarus/dhcp/dhcpd.conf')
o('dhcp_cfg_fname', 'Tartarus.DHCP.DHCPConfigFile', '/etc/dhcp/dhcpd.conf')
del o

init = _Options.init
opts = _Options.get

