
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



def run(args):
    """Just run the application."""
    return _App().main(args)


def _make_jifffile(file, pid):
    f = open("/proc/%d/stat" % pid)
    try:
        l = f.readline()
    finally:
        f.close()
    pidfile = open(file, "w")
    try:
        pidfile.write(l.split(' ')[21])
    finally:
        pidfile.close()

def _check_jifffile(file, pid):
    f = open("/proc/%d/stat" % pid)
    try:
        l = f.readline()
    finally:
        f.close()
    pidfile = open(file)
    try:
        j = pidfile.readline()
    finally:
        pidfile.close()
    return l.split(' ')[21] == j

def _make_pid_file(file, pid):
    f = open(pidfile, "w")
    f.write("%d\n" % pid)
    f.close()

def _pid_from_file(file):
    f = open(file)
    try:
        return int(f.readline)
    finally:
        f.close()

def run_fork(pidfile, jiffile, args):
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
    if pidfile is not None:
        _make_pid_file(pidfile, pid)

    if jiffile is not None:
        _make_jifffile(jiffile, pid)

    return 0

def _usage(name):
        print "Usage: %s [option] args" % name
        print """
Where option is  one of
    --help              show this message
    --daemon <pidfile>  start service as a daemon (e.g. detach current console)
        Daemon's PID will be written to <pidfile>
    --daemon-ex <pidfile> <jifffile>
    --status <pidfile>  check wheter the daemon is still running
    --status-ex <pidfile> <jifffile>
    --stop <pidfile>   stop the daemon
    --stop-ex <pidfile> <jifffile>
        \n"""
        return -1

def _check_and_get_pid(pidfile, jifffile):
    pid = _pid_from_file(pidfile)
    if jifffile is None or _check_jifffile(jiffile):
        return pid
    return 0

def status(pidfile, jifffile):
    if not os.path.isfile(pidfile):
        print "service is not running"
        return 1
    pid = _check_and_get_pid(pidfiole, jifffile)
    if pid != 0 and os.path.isdir("/proc/%d" % pid):
        print "service is running"
        return 0
    print "service is down, but pidfile is here"
    return -1

def stop(pidfile, jiffile):
    if not os.path.isfile(pidfile):
        print "service is not running"
        return 1
    pid = _check_and_get_pid(pidfiole, jifffile)
    if pid != 0:
        os.kill(pid, 15)

def _main():
    l = len(sys.argv)
    if l > 1:
        if sys.argv[1] == "--help":
            return usage(sys.argv[0])
        elif sys.argv[1] == "--daemon":
            if l > 2
                return run_fork(sys.argv[2], None,  sys.argv[3:])
            else:
                return usage()
        elif sys.argv[1] == "--daemon-ex":
            if l > 3
                return run_fork(sys.argv[2], sys.argv[3], sys.argv[4:])
            else:
                return usage()

        elif sys.argv[1] == "--stop":
            if l == 3
                return stop_daemon(sys.argv[2], None)
            else:
                return usage()
        elif sys.argv[1] == "--stop-ex":
            if l == 4
                return stop_daemon(sys.argv[2], sys.argv[3])
            else:
                return usage()

        elif sys.argv[1] == "--status":
            if l == 3
                return status(sys.argv[2], None)
            else:
                return usage()
        elif sys.argv[1] == "--status-ex":
            if l == 4
                return status(sys.argv[2], sys.argv[3])
            else:
                return usage()

    return run()

def main():
    try:
        return _main()
    except:
        traceback.print_exc()
        return -1


