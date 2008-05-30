"""Tartarus.daemon module provides a way of writing services in python.

Such services are intended to run as unix daemons and provide Ice
servants (Ice is Internet Communication Egine -- an object-oriented RPC
developed by Zeroc -- http://www.zeroc.com ).
"""

from __future__ import with_statement
import sys, os, traceback, exceptions, Ice, Tartarus
from Tartarus import logging

_msg_len = 10000


verbose = False


def _report_result(fd, code, msg):
    r"""Private function for internal use.

    Report a result through given file descriptor.

    When starting a daemon, parent process waits on a pipe to read the results
    of child initialization. This function is used to write such results to the
    pipe.
    """
    #if fd is not None and fd > 0:
    try:
        os.write(fd, "%d:%s" % (code, msg[:_msg_len - 20]))
    except Exception:
        if code != 0:
            logging.error(msg)

def _format_exception():
    r"""Private function for internal use.

    Get code and description from occured exception.

    From system information about last ocuured exception it forms a string
    description of the error caused the exception, which can be reported to
    user, and integer error code, which can be, for example, reported to
    operating system as process exit code.

    Returns a pair (code, description).
    """
    (et, ev, tb) = sys.exc_info()
    if not verbose:
        tb = None

    if et is exceptions.SystemExit:
        sys.exit(ev)
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
        msg = str().join(traceback.format_exception(et,ev,tb))

    if not msg.endswith('\n'):
        msg += '\n'

    return (code, msg)

def _report_exception(fd = None):
    r"""Private function for internal use.

    When error occured, it is used to report information on to parent process
    or current logging mechanism.
    """
    (code, msg) = _format_exception()
    _report_result(fd, code, msg)
    return code


class DaemonError(exceptions.Exception):
    """Basic class for exceptions connected with daemon startup."""
    def __init__(self, code, msg):
        self.code = code
        self.message = msg
    def __repr__(self):
        return "%s: %s (%d)" % (
                self.__class__.__name__ , self.message, self.code)


class Daemon(Ice.Application):
    r"""Base class of all Tartarus daemons.

    It provides two hooks for derived classes:
        - start(self, communicator, args) to make derivative initialize
          operation
        - wait() where derived classes should perform their job.

    After calling start(...) it reports the result (succes or, in case
    start(...) trow an exception, failure) to the parent though file desctiptor
    given to it's constructor (if any).
    """
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

        except Exception:
            return _report_exception(self.parent_fd)

        try:
            return self.wait()
        except Exception:
            return _report_exception()



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
        if self.jfile is None:
            return True
        with open("/proc/%d/stat" % pid) as f:
            l = f.readline()
        with open(self.jfile) as jfile:
            j = jfile.readline()
        return long(l.split()[21]) == long(j)

    def _make_pid_file(self, pid):
        with open(self.pidfile, "w") as f:
            f.write("%d\n" % pid)

    def _check_and_get_pid(self):
        if self.pidfile is None:
            raise DaemonError, (2, "please specify pidfile")
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
        except Exception:
            sys.exit(_report_exception(parent_fd))

    def start(self):
        """Start an application as a daemon."""

        (rfd,wfd) = os.pipe()

        if os.fork() == 0:
            os.close(rfd)
            self._run_child(wfd)
            sys.exit(0)

        #parent
        os.close(wfd)
        res = os.read(rfd, _msg_len)
        ind = res.find(':')
        if ind <= 0:
            raise DaemonError, (-1, "Failed to get daemon initialization status")

        code = int(res[:ind])
        msg = res[(ind+1):]
        if (code != 0):
            raise DaemonError, (code, msg)

        pid = int(msg)
        if self.printpid:
            print str(pid)

        if self.pidfile is not None:
            self._make_pid_file(pid)
        if self.jfile is not None:
            self._make_jfile(pid)

        return 0

def _parse_options():
    """Private function for internal use.

    Used by main(...) to parse command-line options. Returns a 3-tuple of
    options object,  an action program was asked to perfom and arguments that
    should be passed farther to child process.
    """
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
            action="store_true", dest = "printpid", default=False,
            help="optput pid of started process to stdout")
    parser.add_option("--noprintpid",
            action="store_false", dest = "printpid", default=False,
            help="do not print pid of started process to stdout (the default)")

    parser.add_option("--chdir",
            action="store_true", dest = "chdir", default=True,
            help="change directory of running daemon to root (the default)")
    parser.add_option("--nochdir",
            action="store_false", dest = "chdir", default=True,
            help="do not change directory of running daemon to root")

    parser.add_option("--closefds",
            action="store_true", dest = "closefds", default=True,
            help="release sandard input, output and error streams"
                    " (the default)")
    parser.add_option("--noclosefds",
            action="store_false", dest = "closefds", default=True,
            help="do not release sandard input, output and error streams")

    parser.add_option("-v", "--verbose",
            action="store_true", default=False,
            help="be more verbose in case of error")

    parser.add_option("--stderr",
            action="store_true", default=False,
            help="log output to stderr instead of system log; "
                 "with --closefds disables most logging messages")

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

    if action[0] == 'status':
        # print status to stderr -- not overridable
        opts.stderr = True

    if not opts.stderr:
        args.append('--Ice.UseSyslog')

    global verbose
    verbose = opts.verbose

    return (opts, action[0], [sys.argv[0]] + args)



def main(what):
    err = None

    try:
        (opts, action, args) = _parse_options()
        if opts.stderr:
            err = sys.stderr

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
    except Exception:
        (code, msg) = _format_exception()
        if err is None:
            import syslog
            syslog.openlog('Tartarus', 0)
            syslog.syslog(msg)
        else:
            try:
                err.write(msg)
            except:
                pass

        return code

