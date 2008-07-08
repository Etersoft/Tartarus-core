
import Ice, Tartarus, unittest, sys, os

__all__ = ['TestBase', 'TestWithUser', 'main', 'load']

Tartarus.modules.trace = 0
Tartarus.slices.trace = 0
Tartarus.slices.path += ["../slice"]

class TestBase(unittest.TestCase):
    def setUp(self):
        args = sys.argv
        if len(sys.argv) < 2 and 'ICE_CONFIG' not in os.environ:
            args.append('--Ice.Config=./config.client')
        self.com = Ice.initialize(args)
        self.I = Tartarus.iface.SysDB
        pr = self.com.propertyToProxy("Tartarus.SysDB.UserManagerPrx")
        self.um = self.I.UserManagerPrx.checkedCast(pr)
        pr = self.com.propertyToProxy("Tartarus.SysDB.GroupManagerPrx")
        self.gm = self.I.GroupManagerPrx.checkedCast(pr)

    def tearDown(self):
        del self.um
        del self.gm
        self.com.destroy()
        del self.com


class TestWithUser(TestBase):
    def setUp(self):
        TestBase.setUp(self)
        g = self.gm.get(1,-1)
        self.gid = g[0].gid
        self.name = ('Test user that does not exist, for '
                        + self.__class__.__name__)

    def tearDown(self):
        try:
            user = self.um.getByName(self.name)
            self.um.delete(user.uid)
        except Exception, e:
            pass
        TestBase.tearDown(self)


def load(*args):
    s = unittest.TestSuite()
    s.addTests((unittest.TestLoader().loadTestsFromTestCase(a)
                for a in args))
    return s

def main(suite, verbosity=0):
    unittest.TextTestRunner(verbosity=verbosity).run(suite)

