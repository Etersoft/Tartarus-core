#!/usr/bin/env python

from testbase import *

class searchNothingTest(TestBase):
    def runTest(self):
        l = self.um.search("%%%%%%%%%", -1)
        self.assertEqual(l, [])

tests = load(searchNothingTest)

if __name__ == '__main__':
    main(tests)
