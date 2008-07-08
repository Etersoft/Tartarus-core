#!/usr/bin/env python

from testbase import *

class getGroupTest(TestBase):
    def testGet(self):
        #just enshure this does not throw:
        self.gm.get(-1, -1)
        self.gm.get(2, 2)

    def testNameUnknown(self):
        self.assertRaises(self.I.NotFound,
                self.gm.getByName,
                "Test group that doesn't exist")


tests = load(getGroupTest)

if __name__ == '__main__':
    main(tests)

