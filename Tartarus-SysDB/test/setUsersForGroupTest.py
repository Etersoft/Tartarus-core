#!/usr/bin/env python

from testbase import *

class setUsersGroupTest(TestWithGroup):
    def testEmpty(self):
        gr = self.I.GroupRecord(-1, self.gname, self.gname)
        gr.gid = self.gm.create(gr)

        ids = self.gm.getUsers(gr.gid)
        self.assertEqual(ids, [])

        self.assertRaises(self.ICore.NotFoundError
                self.gm.delUsers,
                gr.gid, [1,2,3,4,5])

        self.gm.delete(gr.gid)

    def testSetAndDel(self):
        uids = [ u.uid for u in self.um.get(10, -1) ]
        uids.sort()

        gr = self.I.GroupRecord(-1, self.gname, self.gname)
        gr.gid = self.gm.create(gr)

        self.gm.setUsers(gr.gid, uids)
        uids2 = self.gm.getUsers(gr.gid)
        uids2.sort()

        self.assertEqual(uids, uids2)

        self.gm.delUsers(gr.gid, uids[:-1]) # all but last

        ids = self.gm.getUsers(gr.gid)
        self.gm.delete(gr.gid)
        self.assertEqual(ids, [uids[-1]])

    def testAddAndSet(self):
        uids = [ u.uid for u in self.um.get(10, -1) ]
        #uids.sort()

        gr = self.I.GroupRecord(-1, self.gname, self.gname)
        gr.gid = self.gm.create(gr)

        self.gm.addUsers(gr.gid, uids)

        ids = self.gm.getGroupsForUserId(uids[0])
        self.failUnless(gr.gid in ids)

        self.gm.setUsers(gr.gid, [uids[0]])

        ids = self.gm.getUsers(gr.gid)
        self.gm.delete(gr.gid)
        self.assertEqual(ids, [uids[0]])


tests = load(setUsersGroupTest)

if __name__ == '__main__':
    main(tests)

