#!/usr/bin/env python

from testbase import *

class searchNothingTest(TestBase):
    def testUsers(self):
        l = self.um.search("%%%%%%%%%", -1)
        self.assertEqual(l, [])

    def testGroups(self):
        l = self.gm.search("%%%%%%%%%", -1)
        self.assertEqual(l, [])

tests = load(searchNothingTest)

if __name__ == '__main__':
    main(tests)
