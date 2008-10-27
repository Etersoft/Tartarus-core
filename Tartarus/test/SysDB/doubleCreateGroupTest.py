#!/usr/bin/env python

from testbase import *

class doubleCreateGroupTest(TestWithGroup):
    def runTest(self):
        gr = self.I.GroupRecord(-1, self.gname, self.gname)
        id = self.gm.create(gr)
        self.gm.delete(id)
        id2 = self.gm.create(gr)
        self.gm.delete(id2)
        self.assertNotEqual(id, id2)



tests = load(doubleCreateGroupTest)

if __name__ == '__main__':
    main(tests)
