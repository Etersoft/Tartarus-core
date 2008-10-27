#!/usr/bin/env python

from testbase import *

class modifyGroupTest(TestWithGroup):
    def runTest(self):
        gr = self.I.GroupRecord(-1, self.gname, self.gname)
        gr.gid = self.gm.create(gr)

        gr2 = self.gm.getByName(self.gname)
        self.assertEqual(gr, gr2)

        gr.fullname = self.gname + ', modified'
        self.gm.modify(gr)

        gr2 = self.gm.getByName(self.gname)
        self.assertEqual(gr, gr2)

        self.gm.delete(gr.gid)

tests = load(modifyGroupTest)

if __name__ == '__main__':
    main(tests)

