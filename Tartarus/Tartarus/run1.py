
import os, sys, logging, traceback, Ice, Tartarus

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
    def __init__(fd = -1):
        self.parent_fd = fd

    def load_module(self, modname, path):
        if not os.path.isdir(path):
            logging.debug("Skipping file %s", path)
            return

        # we load only modules which names start with big latin letters
        if m[0] < 'A' or m[0] > 'Z':
            logging.debug("Skipping directory %s", path)
            return

        logging.info("Loading module %s.", % m)
        modname = "Tartarus.%s" % m
        __import__(modname)
        module = sys.modules["modname"]
        module.init(adapter)


    def apply_properties(self, props):
        Tartarus.module_path += \
            props.propertiesForPrefix('Tartarus.AddModulePath.').itervalues()
        logging.debug("Tartarus module path is now %s.", Tartarus.module_path)
        Tartarus.slices.path += \
            props.propertiesForPrefix('Tartarus.AddSlicePath.').itervalues()
        logging.debug("Tartarus slice path is now %s.", Tartarus.slices_path)


    def run(self, args):
        try:
            self.shutdownOnInterrupt()
            Ice.setProcessLogger(comm.getLogger())
            comm = self.communicator()
            adapter = comm.createObjectAdapter("TartarusAdapter")

            self.apply_properties(comm.getProperties())

            Tartarus.__path__ += Tartarus.module_path
            for dir in Tartarus.module_path:
                for m in os.listdir(dir):
                    self.load_module(m, os.path.join(dir,m))

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
                logging.critical(msg)
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
        logging.critical(rfd[1:])
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

