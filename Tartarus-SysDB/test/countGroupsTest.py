#!/usr/bin/env python

from testbase import *

class countGroupsTest(TestBase):
    def testCount(self):
        c = self.gm.count()
        u = self.gm.get(-1, -1)
        self.assertEqual(c, len(u))


tests = load(countGroupsTest)

if __name__ == '__main__':
    main(tests)

