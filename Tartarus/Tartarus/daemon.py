
from __future__ import with_statement
import sys, os, traceback, exceptions, Ice, Tartarus
from Tartarus import logging

_msg_len = 10000


def _format_exception():
    (et, ev, tb) = sys.exc_info()
    try:
        return "%s" % ev.reason
    except:
        pass

    return traceback.format_exception(et,ev,None)


class DaemonException(exceptions.Exception):
    def __init__(self, code, msg):
        self.code = code
        self.message = msg
    def __repr__(self):
        return self.__class__.__name__ + (": %s" % args)


class Daemon(Ice.Application):
    # clients will override this two:
    def start(self, comm, args):
        pass
    def wait(self):
        pass

    def __init__(self, fd=None):
        self.parent_fd = fd
        Ice.Application.__init__(self)

    def run(self, args):
        try:
            self.shutdownOnInterrupt()
            comm = self.communicator()
            Ice.setProcessLogger(comm.getLogger())

            self.start(self.communicator(), args)

            if self.parent_fd is not None:
                os.write(self.parent_fd, '\0%d' % os.getpid())
        except:
            msg = _format_exception()
            if self.parent_fd is not None:
                os.write(self.parent_fd, chr(1) + msg[:_msg_len])
            else:
                logging.error(msg)
            return 1

        try:
            return self.wait()
        except:
            msg = _format_exception()
            logging.error(msg)
            return -1


class DaemonController(object):
    """A class to control the Daemon Of Tartarus.

    The code is written under one very strong assumption: the second field in
    /proc/<pid>/stat does not contain space characters. This is true for any
    python program, because it's name is the name of python executable
    (python).
    """
    def __init__(self, what, args, pidfile = None, jfile = None, printpid=False):
        self.args = args
        self.pidfile = pidfile
        self.jfile = jfile
        self.what = what
        self.printpid = printpid

    def _make_jfile(self, pid):
        with open("/proc/%d/stat" % pid) as f:
            j = f.readline().split()[21]
        with open(self.jfile, "w") as jfile:
            jfile.write(j)
            jfile.write('\n')

    def _check_jfile(self, pid):
        with open("/proc/%d/stat" % pid) as f:
            l = f.readline()
        with open(self.jfile) as jfile:
            j = jfile.readline()

        return l.split()[21] == j

    def _make_pid_file(self, pid):
        with open(self.pidfile, "w") as f:
            f.write("%d\n" % pid)

    def _check_and_get_pid(self):
        if not os.path.isfile(self.pidfile):
            raise DaemonException, (-1, "service is not running")
        with open(self.pidfile) as f:
            pid = int(f.readline())
        if not os.path.isdir("/proc/%d" % pid):
            raise DaemonException, (1, "service is not running, but pidfile exists")

        if self.jfile is not None and not self._check_jfile(pid):
            raise DaemonException, (1, "service is not running, but pidfile exists")

        return pid

    def status(self):
        return self._check_and_get_pid()

    def stop(self):
        try:
            pid = self._check_and_get_pid()
            os.kill(pid, 15)
        finally:
            if self.pidfile and os.path.isfile(self.pidfile):
                os.unlink(self.pidfile)
            if self.jfile and os.path.isfile(self.jfile):
                os.unlink(self.jfile)
        return 0

    def _run_child(self, parent_fd):
        try:
            import signal
            signal.signal(signal.SIGHUP, signal.SIG_IGN)

            os.setsid()
            os.chdir('/')

            devnull = os.open("/dev/null", os.O_RDWR, 0)
            if (devnull > 0):
                os.dup2(devnull,0)
                os.dup2(devnull,1)
                os.dup2(devnull,2)

            if os.fork() > 0:
                sys.exit(0)

            sys.exit(self.what(parent_fd).main(self.args))
        except OSError, err:
            os.write(parent_fd, chr(err.errno) + err.strerror)
            sys.exit(-1)
        except:
            if sys.exc_info()[0] is SystemExit:
                raise
            msg = _format_exception()
            os.write(parent_fd, chr(1) + msg[:_msg_len])
            sys.exit(-1)




    def start(self):
        """Start an application as a daemon."""

        (rfd,wfd) = os.pipe()

        if os.fork() == 0:
            os.close(rfd)
            self._run_child(wfd)
            sys.exit(0)

        #parent
        os.close(wfd)
        res = os.read(rfd, _msg_len + 3)
        if len(res) < 1:
            raise DaemonException, (-1, "Failed to get daemon initialization status")
        code = ord(res[0])
        msg = res[1:]
        if (code != 0):
            raise DaemonException, (code, msg)

        pid = int(msg)
        if (self.printpid):
            print str(pid)

        if self.pidfile is not None:
            self._make_pid_file(pid)
        if self.jfile is not None:
            self._make_jfile(pid)

        return 0

def _parse_options():
    import optparse
    usage = "usage: %prog [options] [start|stop|status] [-- [ice_opts]]"
    version = "%prog 0.0.1"

    parser = optparse.OptionParser(usage=usage, version=version)

    parser.add_option("-p", "--pidfile",
            help="store id of started process to file PIDFILE")
    parser.add_option("-j", "--jfile",
            help="create a jfile JFILE")
    parser.add_option("-o", "--printpid",
            action="store_true",
            help="Optput pid of started process to strout")

    try:
        sp = sys.argv.index('--')
        our_args = sys.argv[1:sp]
        args = sys.argv[(sp+1):]
    except ValueError:
        our_args = sys.argv[1:]
        args = []

    (opts, action) = parser.parse_args(our_args)
    if len(action) != 1 or action[0] not in ['start','stop','status','run']:
        parser.error("Don't know what to do!")

    return (opts, action[0], [sys.argv[0]] + args)



def main(what):
    try:
        (opts, action, args) = _parse_options()
        if action == 'run':
            return what().main(args)
        dc = DaemonController(what, args, opts.pidfile, opts.jfile, opts.printpid)
        if action == 'start':
            return dc.start()
        elif action == 'stop':
            return dc.stop()
        elif action == 'status':
            if dc.status():
                print "service is running"
                return 0

        raise DaemonError, (-1, "This can't happen!")
    except DaemonException, ex:
        sys.stderr.write("Error: ")
        sys.stderr.write(ex.message)
        sys.stderr.write('\n')
        return ex.code



