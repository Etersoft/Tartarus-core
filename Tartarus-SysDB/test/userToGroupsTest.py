#!/usr/bin/env python

from testbase import *

class userToGroupsTest(TestWithUser):
    def setUp(self):
        TestWithUser.setUp(self)
        self.ur = self.I.UserRecord(-1, self.gid, self.name, self.name)
        groups = self.gm.get(10, -1)
        self.gids = [g.gid for g in groups if g.gid != self.gid]
        self.ngid = self.gids[0]
        self.gids.sort()

    def tearDown(self):
        del self.ur
        del self.gids
        TestWithUser.tearDown(self)

    def testAddDell(self):
        self.ur.uid = self.um.create(self.ur)
        self.gm.addUserToGroups(self.ur.uid, self.gids)
        gids2 = self.gm.getGroupsForUserId(self.ur.uid)
        gids2.remove(self.ur.gid)
        gids2.sort()
        self.assertEqual(self.gids, gids2)

        self.gm.delUserFromGroups(self.ur.uid, [self.ngid])
        gids2 = self.gm.getGroupsForUserId(self.ur.uid)
        # self.ngid in self.gids and self.gid in gids2:
        self.assertEqual(len(self.gids), len(gids2))
        self.failIf(self.ngid in gids2)
        self.um.delete(self.ur.uid)

    def testDeleteUserFromStrangeGroup(self):
        uid = self.um.create(self.ur)
        self.assertRaises(self.I.NotFound,
                self.gm.delUserFromGroups,
                uid, [self.ngid])
        self.um.delete(uid)

    def testDeleteUserFromGroupsPrimary(self):
        uid = self.um.create(self.ur)
        self.assertRaises(self.I.DBError,
                self.gm.delUserFromGroups,
                uid, [self.gid])
        self.um.delete(uid)

    def testDeleteUserPrimary(self):
        uid = self.um.create(self.ur)
        self.assertRaises(self.I.DBError,
                self.gm.delUsers,
                self.gid, [uid])
        self.um.delete(uid)

tests = load(userToGroupsTest)

if __name__ == '__main__':
    main(tests)

