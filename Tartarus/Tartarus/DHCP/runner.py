import time
import os
import signal
import resource
from subprocess import Popen, PIPE
from enum import Enum

Status = Enum('RUN', 'STOP')

class Runner:
    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance
    def __init__(self):
        self.__program = 'dhcpd'
        self.__pid = None
        fname = opts().dhcp_cfg_fname
        cmd = 'dhcpd -f -q -cf ' + fname
        testcmd = 'dhcpd -t -cf ' + fname
        self.__args = cmd.split()
        self.__testargs = testcmd.split()
    def start(self):
        if self.status() == Status.RUN:
            raise StartError('dhcpd allready started')
        result, msg = self.testCfg()
        if not result:
            msg = 'Can\'t start dhcpd: config file checking failed\n\n' + msg
            raise StartError(msg)
        self.__pid = _spawn(self.__program, self.__args)
        time.sleep(1)
        if self.status() != Status.RUN:
            msg = 'dhcpd was started, but it status is not RUN'
            raise StartError(msg)
    def stop(self):
        if self.status() == Status.STOP:
            return
        os.kill(self.__pid, signal.SIGTERM)
        self.__waitpid()
    def status(self):
        if self.__pid is None:
            return Status.STOP
        statfile = '/proc/%d/stat' % self.__pid
        if os.path.exists(statfile):
            statcontent = open(statfile).read()
            stat = statcontent.split()
            if stat[1] == '(dhcpd)' and stat[2] != 'Z':
                return Status.RUN
            if stat[1] == '(dhcpd)' and stat[2] == 'Z':
                self.__waitpid()
        return Status.STOP
    def testCfg(self):
        sp = Popen(self.__testargs, stderr=PIPE)
        _, err = sp.communicate()
        return sp.returncode == 0, err
    def __waitpid(self):
        os.waitpid(self.__pid, 0)
        self.__pid = None
    __instance = None

class StartError(RuntimeError):
    def __init__(self, msg):
        RuntimeError.__init__(self, msg)

def _spawn(program, args):
    pid = os.fork()
    if pid: return pid
    _exec(program, args)

def _exec(program, args):
    if os.path.exists('/proc/self/fd'):
        for i in os.listdir('/proc/self/fd'):
            if int(i) not in (0, 1, 2):
                try: os.close(int(i))
                except: pass
    else:
        try:
            maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
        except:
            maxfd = 255
        for i in xrange(maxfd):
            if i not in (0, 1, 2):
                try: os.close(int(i))
                except: pass
    os.execvp(program, args)

from options import opts

