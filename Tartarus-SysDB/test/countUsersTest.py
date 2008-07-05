#!/usr/bin/env python

from testbase import *

class countTest(TestBase):
    name = 'Test user that does not exist, for countTest'
    def setUp(self):
        TestBase.setUp(self)
        g = self.gm.get(1,-1)
        self.gid = g[0].gid

    def runTest(self):
        c1 = self.um.count()
        ur = self.I.UserRecord(-1, self.gid, self.name, self.name)
        id = self.um.create(ur)
        c2 = self.um.count()
        self.um.delete(id)
        c3 = self.um.count()
        self.assertEqual(c1, c3)
        self.assertEqual(c1, c2- 1)

    def tearDown(self):
        try:
            user = self.um.getByName(self.name)
            self.um.delete(user.uid)
        except Exception, e:
            pass
        TestBase.tearDown(self)


tests = load(countTest)

if __name__ == '__main__':
    main(tests)
