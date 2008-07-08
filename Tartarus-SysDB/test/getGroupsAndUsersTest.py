#!/usr/bin/env python

from testbase import *

class getGroupsAndUsersTest(TestBase):
    def setUp(self):
        TestBase.setUp(self)
        self.ur = self.um.get(1,-1)[0]

    def testGet(self):
        gr1 = self.gm.getById(self.ur.gid)
        gr2 = self.gm.getByName(gr1.name)
        self.assertEqual(gr1, gr2)
        self.assertEqual(gr1.gid, self.ur.gid)

    def testGetFor(self):
        gr1 = self.gm.getGroupsForUserName(self.ur.name)
        gr2 = self.gm.getGroupsForUserId(self.ur.uid)
        self.failIf(self.ur.gid not in gr1)
        gr1.sort()
        gr2.sort()
        self.assertEqual(gr1, gr2)

    def testGetUsers(self):
        uids = self.gm.getUsers(self.ur.gid)
        self.failUnless(self.ur.uid in uids)

    def tearDown(self):
        del self.ur
        TestBase.tearDown(self)

tests = load(getGroupsAndUsersTest)

if __name__ == '__main__':
    main(tests)

