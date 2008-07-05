#!/usr/bin/env python

from testbase import *

class getUserTest(TestBase):
    def testGet(self):
        l = self.um.get(0, 2)
        self.assertEqual(l, [])

    def testUsers(self):
        l = self.um.getUsers([])
        self.assertEqual(l, [])


tests = load(getUserTest)

if __name__ == '__main__':
    main(tests)
