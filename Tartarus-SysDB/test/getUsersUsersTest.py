#!/usr/bin/env python

from testbase import *

class getUserTest(TestBase):
    def runTest(self):
        us = self.um.get(10, -1)
        self.failIf(len(us) == 0)
        self.failIf(len(us) > 10)

        ids = [ u.uid for u in us ]
        us2 = self.um.getUsers(ids)

        us.sort()
        us2.sort()
        self.assertEqual(us, us2)


tests = load(getUserTest)

if __name__ == '__main__':
    main(tests)

