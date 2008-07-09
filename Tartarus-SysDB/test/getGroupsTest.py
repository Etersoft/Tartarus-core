#!/usr/bin/env python

from testbase import *

def getGid(group):
    return group.gid

class getGroupTest(TestBase):
    def testGet(self):
        #just enshure this does not throw:
        self.gm.get(-1, -1)
        self.gm.get(2, 2)

    def testNameUnknown(self):
        self.assertRaises(self.I.NotFound,
                self.gm.getByName,
                "Test group that doesn't exist")

    def testGetGroups(self):
        groups = self.gm.get(10,-1)
        groups.sort(key=getGid)
        gids = [g.gid for g in groups]
        groups2 = self.gm.getGroups(gids)
        groups2.sort(key=getGid)
        self.assertEqual(groups, groups2)


tests = load(getGroupTest)

if __name__ == '__main__':
    main(tests)

