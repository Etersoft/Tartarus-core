#!/usr/bin/env python

from testbase import *

class doubleCreateTest(TestWithUser):
    def runTest(self):
        ur = self.I.UserRecord(-1, self.gid, self.name, self.name)
        id = self.um.create(ur)
        self.um.delete(id)
        id2 = self.um.create(ur)
        self.um.delete(id2)
        self.assertNotEqual(id, id2)



tests = load(doubleCreateTest)

if __name__ == '__main__':
    main(tests)
