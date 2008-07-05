#!/usr/bin/env python

from testbase import *

class modifyTest(TestBase):
    name = 'Test user that does not exist, for modifyTest'
    def setUp(self):
        TestBase.setUp(self)
        g = self.gm.get(1,-1)
        self.gid = g[0].gid

    def runTest(self):
        ur = self.I.UserRecord(-1, self.gid, self.name, self.name)
        ur.uid = self.um.create(ur)

        ur2 = self.um.getByName(self.name)
        self.assertEqual(ur, ur2)

        ur.fullname = self.name + ', modified'
        self.um.modify(ur)

        ur2 = self.um.getByName(self.name)
        self.assertEqual(ur, ur2)

        self.um.delete(ur.uid)

    def tearDown(self):
        try:
            user = self.um.getByName(self.name)
            self.um.delete(user.uid)
        except Exception, e:
            pass
        TestBase.tearDown(self)


tests = load(modifyTest)

if __name__ == '__main__':
    main(tests)
