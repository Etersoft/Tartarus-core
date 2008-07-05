#!/usr/bin/env python

from testbase import *

class getUnknownUserByNameTest(TestBase):
    def runTest(self):
        self.assertRaises(self.I.NotFound, self.um.getByName,
                'NonExistentUser12')

tests = load(getUnknownUserByNameTest)

if __name__ == '__main__':
    main(tests)

