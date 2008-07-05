#!/usr/bin/env python

from testbase import *

class doubleCreateTest(TestBase):
    name = 'Test user that does not exist, for doubleCreateTest'
    def setUp(self):
        TestBase.setUp(self)
        g = self.gm.get(1,-1)
        self.gid = g[0].gid

    def runTest(self):
        ur = self.I.UserRecord(-1, self.gid, self.name, self.name)
        id = self.um.create(ur)
        self.um.delete(id)
        id2 = self.um.create(ur)
        self.um.delete(id2)
        self.assertNotEqual(id, id2)

    def tearDown(self):
        try:
            user = self.um.getByName(self.name)
            self.um.delete(user.uid)
        except Exception, e:
            pass
        TestBase.tearDown(self)


tests = load(doubleCreateTest)

if __name__ == '__main__':
    main(tests)
