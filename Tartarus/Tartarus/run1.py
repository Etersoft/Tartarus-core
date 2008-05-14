
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

    def apply_properties(self, props):
        Tartarus.modules.trace = props.getPropertyAsInt("Tartarus.modules.Trace")
        Tartarus.slices.trace = props.getPropertyAsInt("Tartarus.import.Trace")
        Tartarus.modules.path += \
            props.getPropertiesForPrefix('Tartarus.addModulePath.').itervalues()
        Tartarus.slices.path += \
            props.getPropertiesForPrefix('Tartarus.addSlicePath.').itervalues()


    def run(self, args):
        try:
            self.shutdownOnInterrupt()
            comm = self.communicator()
            Ice.setProcessLogger(comm.getLogger())
            adapter = comm.createObjectAdapter("TartarusAdapter")

            self.apply_properties(comm.getProperties())

            Tartarus.modules.load_modules1(adapter)

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

