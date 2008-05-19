
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


    def start(self, comm, args):
        self.adapter = comm.createObjectAdapter("TartarusAdapter")
        self.apply_properties(comm.getProperties())
        modules.load_modules1(self.adapter)
        self.adapter.activate()


    def wait(self):
        self.adapter.waitForDeactivate()
        return 0


def main():
    import sys
    sys.exit(daemon.main(_App))

