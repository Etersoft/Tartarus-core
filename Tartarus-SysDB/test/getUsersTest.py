#!/usr/bin/env python

from testbase import *

class getUserTest(TestBase):
    def runTest(self):
        #just enshure this does not throw:
        self.um.get(-1, -1)
        self.um.get(2, 2)

tests = load(getUserTest)

if __name__ == '__main__':
    main(tests)
