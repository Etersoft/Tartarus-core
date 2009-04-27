#!/usr/bin/env python


from testbase import *

class badGroupTest(TestWithGroup):
    def testCreate(self):
        gr = self.I.GroupRecord(-1, '1' + self.gname, self.gname)
        self.assertRaises(self.ICore.ValueError, self.gm.create, gr)

    def testModify(self):
        gr = self.I.GroupRecord(-1, self.gname, self.gname)
        gr.uid = self.gm.create(gr)

        gr.name = '1' + self.gname + ', modified'
        self.assertRaises(self.ICore.ValueError, self.gm.modify, gr)

tests = load(badGroupTest)

if __name__ == '__main__':
    main(tests)

