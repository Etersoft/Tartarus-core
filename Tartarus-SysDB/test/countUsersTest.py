#!/usr/bin/env python

from testbase import *

class countUsersTest(TestWithUser):
    def testCreateRemove(self):
        c1 = self.um.count()
        ur = self.I.UserRecord(-1, self.gid, self.name, self.name)
        id = self.um.create(ur)
        c2 = self.um.count()
        self.um.delete(id)
        c3 = self.um.count()
        self.assertEqual(c1, c3)
        self.assertEqual(c1, c2- 1)

    def testGetUsers(self):
        c = self.um.count()
        u = self.um.get(-1, -1)
        self.assertEqual(c, len(u))


tests = load(countUsersTest)

if __name__ == '__main__':
    main(tests)

