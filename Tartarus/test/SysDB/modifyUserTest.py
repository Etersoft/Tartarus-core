#!/usr/bin/env python

from testbase import *

class modifyUserTest(TestWithUser):
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

tests = load(modifyUserTest)

if __name__ == '__main__':
    main(tests)

