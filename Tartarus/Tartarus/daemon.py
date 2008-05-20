
from __future__ import with_statement
import sys, os, traceback, exceptions, Ice, Tartarus
from Tartarus import logging

_msg_len = 10000


def _report_result(fd, code, msg):
    #if fd is not None and fd > 0:
    try:
        os.write(fd, chr(code) + msg[:_msg_len])
    except:
        if code != 0:
            logging.error(msg)

def _format_exception():
    (et, ev, tb) = sys.exc_info()

    if et is exceptions.SystemExit:
        raise
    elif et is DaemonError:
        code = ev.code
        msg = ev.message
    elif et is Ice.InitializationException:
        code = -1
        msg = "Failed to initialize runtime: %s" % ev.reason
    elif et is OSError:
        code =  ev.errno
        msg = "OS Error: %s" % ev.strerror
    else:
        code =  -1
        msg = traceback.format_exception(et,ev,None)
    return (code, msg)

def _report_exception(fd = None):
    (code, msg) = _format_exception()
    _report_result(fd, code, msg)
    sys.exit(code)


class DaemonError(exceptions.Exception):
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

            _report_result(self.parent_fd, 0, "%d" % os.getpid())

        except:
            _report_exception(parent_fd)

        try:
            sys.exit(self.wait())
        except:
            _report_exception()



class DaemonController(object):
    """A class to control the Daemon Of Tartarus.

    The code is written under one very strong assumption: the second field in
    /proc/<pid>/stat does not contain space characters. This is true for any
    python program, because it's name is the name of python executable
    (python).
    """
    def __init__(self, what, args, opts):
        self.args = args
        self.what = what
        self.pidfile = opts.pidfile
        self.jfile = opts.jfile
        self.printpid = opts.printpid
        self.chdir = opts.chdir
        self.closefds = opts.closefds

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
        return long(l.split()[21]) == long(j)

    def _make_pid_file(self, pid):
        with open(self.pidfile, "w") as f:
            f.write("%d\n" % pid)

    def _check_and_get_pid(self):
        if not os.path.isfile(self.pidfile):
            raise DaemonError, (-1, "service is not running")
        with open(self.pidfile) as f:
            pid = int(f.readline())
        if not os.path.isdir("/proc/%d" % pid):
            raise DaemonError, (1, "service is not running, but pidfile exists")

        if self.jfile is not None and not self._check_jfile(pid):
            raise DaemonError, (1, "service is not running, but pidfile exists")

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
            if self.chdir:
                os.chdir('/')

            if self.closefds:
                devnull = os.open("/dev/null", os.O_RDWR, 0)
                os.dup2(devnull,0)
                os.dup2(devnull,1)
                os.dup2(devnull,2)

            if os.fork() > 0:
                sys.exit(0)

            sys.exit(self.what(parent_fd).main(self.args))
        except:
            _report_exception(parent_fd)

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
            raise DaemonError, (-1, "Failed to get daemon initialization status")
        code = ord(res[0])
        msg = res[1:]
        if (code != 0):
            raise DaemonError, (code, msg)

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
    usage = "usage: %prog [options] [action] [-- [ice_opts]]"
    description = ("Available actions are start, stop, status and run. " +
                    "When action is 'run', all [options] are ignored.")
    version = "%prog 0.0.1"

    parser = optparse.OptionParser(
            usage=usage,
            version=version,
            description=description)

    parser.add_option("-p", "--pidfile",
            help="store id of started process to file PIDFILE")
    parser.add_option("-j", "--jfile",
            help="create a jfile JFILE")
    parser.add_option("-o", "--printpid",
            action="store_true", dest = "printpid", default="False",
            help="optput pid of started process to stdout")
    parser.add_option("--noprintpid",
            action="store_false", dest = "printpid", default="False",
            help="do not print pid of started process to stdout (the default)")

    parser.add_option("--chdir",
            action="store_true", dest = "chdir", default="True",
            help="change directory of running daemon to root (the default)")
    parser.add_option("--nochdir",
            action="store_false", dest = "chdir", default="True",
            help="do not change directory of running daemon to root")

    parser.add_option("--closefds",
            action="store_true", dest = "closefds", default="True",
            help="release sandard input, output and error streams"
                    " (the default)")
    parser.add_option("--noclosefds",
            action="store_false", dest = "closefds", default="True",
            help="do not release sandard input, output and error streams")

    try:
        sp = sys.argv.index('--')
        our_args = sys.argv[1:sp]
        args = sys.argv[(sp+1):]
    except ValueError:
        our_args = sys.argv[1:]
        args = []

    (opts, action) = parser.parse_args(our_args)
    if len(action) != 1 or action[0] not in ['start','stop','status','run']:
        if "print-opts" in action:
            print "DEBUG: OPTIONS: %s,  %s, %s" % (opts, action, args)
        parser.error("Don't know what to do!")

    return (opts, action[0], [sys.argv[0]] + args)



def main(what):
    try:
        (opts, action, args) = _parse_options()
        if action == 'run':
            return what().main(args)
        dc = DaemonController(what, args, opts)
        if action == 'start':
            return dc.start()
        elif action == 'stop':
            return dc.stop()
        elif action == 'status':
            if dc.status():
                print "service is running"
                return 0

        raise DaemonError, (-1, "This can't happen!")
    except:
        (code, msg) = _format_exception()
        sys.stderr.write("%s\n" % msg)
        return code



