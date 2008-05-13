
import os, sys, traceback, Ice, Tartarus

from Tartarus import logging

_msg_len = 10000

#
# TODO: Put this comment to a place where documentation belongs.
#
# FORKING.
#
# We use the following protocol: before forking, a process creates pipe via
# os.pipe function. After forking, child does the initialization, 
# and writes to the pipe a single byte, a zero, if it successfully started.
# On error, it writes to the pipe a single non-zero byte (a error code?)
# and the error message, but the message shold not be longer then _msg_len.
# Parent proccess reads from the pipe, and so blocks until child finishes
# initialization or fails.
#




class _App(Ice.Application):
    def __init__(self, fd = -1):
        self.parent_fd = fd

    def load_module(self, modname, path, adapter):
        if not os.path.isdir(path):
            logging.trace(__name__, "Skipping file %s" % path, Tartarus.trace_load)
            return

        # we load only modules which names start with big latin letters
        if modname[0] < 'A' or modname[0] > 'Z':
            logging.trace(__name__, "Skipping directory %s" % path, Tartarus.trace_load)
            return

        logging.trace(__name__, "Loading module %s." % modname, Tartarus.trace_load)
        modname = "Tartarus.%s" % modname
        __import__(modname)
        module = sys.modules[modname]
        module.init(adapter)


    def apply_properties(self, props):
        Tartarus.trace_import = props.getPropertyAsInt("Tartarus.TraceImport")
        Tartarus.trace_load = props.getPropertyAsInt("Tartarus.TraceLoad")
        Tartarus.module_path += \
            props.getPropertiesForPrefix('Tartarus.AddModulePath.').itervalues()
        logging.trace(__name__,
                "Tartarus module path is now %s." % Tartarus.module_path,
                Tartarus.trace_import)
        Tartarus.slices.path += \
            props.getPropertiesForPrefix('Tartarus.AddSlicePath.').itervalues()
        logging.trace(__name__,
                "Tartarus slice path is now %s." % Tartarus.slices.path,
                Tartarus.trace_load)


    def run(self, args):
        try:
            self.shutdownOnInterrupt()
            comm = self.communicator()
            Ice.setProcessLogger(comm.getLogger())
            adapter = comm.createObjectAdapter("TartarusAdapter")

            self.apply_properties(comm.getProperties())

            Tartarus.__path__ += Tartarus.module_path
            for dir in Tartarus.module_path:
                if not os.path.isdir(dir):
                    logging.warning(
                            "Directory from Tartarus.modpath not found: %s"
                            % dir)
                    continue
                for m in os.listdir(dir):
                    self.load_module(m, os.path.join(dir,m), adapter)

            adapter.activate()
            if self.parent_fd > 0:
                os.write(self.parent_fd, '\0')

            adapter.waitForDeactivate()
            return 0

        except:
            msg = traceback.format_exc()
            if self.parent_fd > 0:
                os.write(self.parent_fd, chr(1))
                os.write(self.parent_fd, msg[:_msg_len])
            else:
                logging.error(msg)
            return 1




def run():
    """Just run the application."""
    return _App().main(sys.argv)


def run_fork(pidfile, args):
    """Start an application as a daemon."""
    (rfd,wfd) = os.pipe()
    pid = os.fork()

    if pid == 0:
        #child
        os.setsid()
        os.close(rfd)
        return _App(wfd).main(args)

    #parent
    os.close(wfd)
    res = os.read(rfd, _msg_len + 3)
    code = ord(res[0])
    if (code != 0):
        logging.error(rfd[1:])
        return code

    #make pid file
    f = open(pidfile, "w")
    f.write("%d\d" % pid)
    f.close()
    return 0


def main():
    if sys.argv[0] == "--help":
        print "Usage: %s [--pidfile filename] args"
        return -1
    elif sys.argv[0] == "--pidfile":
        return run_fork(sys.argv[1], sys.argv[2:])

    return run()

