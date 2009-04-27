#!/usr/bin/env python


from testbase import *

class badUserTest(TestWithUser):
    def testCreate(self):
        ur = self.I.UserRecord(-1, self.gid, '1' + self.name,
                               self.name, '/bin/bash')
        self.assertRaises(self.ICore.ValueError, self.um.create, ur)

    def testModify(self):
        ur = self.I.UserRecord(-1, self.gid, self.name,
                               self.name, '/bin/bash')
        ur.uid = self.um.create(ur)

        ur2 = self.um.getByName(self.name)
        self.assertEqual(ur, ur2)

        ur.name = '1' + self.name + ', modified'
        self.assertRaises(self.ICore.ValueError, self.um.modify, ur)

tests = load(badUserTest)

if __name__ == '__main__':
    main(tests)

