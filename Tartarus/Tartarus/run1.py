
import Tartarus

from Tartarus import daemon, modules


class _App(daemon.Daemon):
    def apply_properties(self, props):
        Tartarus.modules.trace = props.getPropertyAsInt("Tartarus.modules.Trace")
        Tartarus.slices.trace = props.getPropertyAsInt("Tartarus.import.Trace")
        Tartarus.modules.path += \
            props.getPropertiesForPrefix('Tartarus.addModulePath.').itervalues()
        Tartarus.slices.path += \
            props.getPropertiesForPrefix('Tartarus.addSlicePath.').itervalues()


    def __init__(self, comm, args):
        self.adapter = comm.createObjectAdapter("TartarusAdapter")
        props = comm.getProperties()
        self.apply_properties(props)
        modules.load_modules1(self.adapter)
        if props.getPropertyAsIntWithDefault('Ice.InitPlugins',1) == 0:
            import IceSSL
            IceSSL.initializePlugins(comm)
        self.adapter.activate()


    def run(self):
        self.adapter.waitForDeactivate()
        return 0


def main():
    import sys
    sys.exit(daemon.main(_App))

