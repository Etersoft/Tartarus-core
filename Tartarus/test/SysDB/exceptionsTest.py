#!/usr/bin/env python


from testbase import *

class excepionUserTest(TestWithUser):
    def testCreate(self):
        ur = self.I.UserRecord(-1, self.gid, self.name,
                               self.name, '/bin/bash')
        self.um.create(ur)
        self.assertRaises(self.ICore.AlreadyExistsError,
                          self.um.create, ur)

    def testModify(self):
        ur = self.I.UserRecord(-1, self.gid, self.name,
                               self.name, '/bin/bash')
        ur.uid = self.um.create(ur)

        ur2 = self.um.getByName(self.name)
        self.assertEqual(ur, ur2)

        ur.name = "sysadmin" # this user already exists
        self.assertRaises(self.ICore.AlreadyExistsError,
                          self.um.modify, ur)



class exceptionGroupTest(TestWithGroup):
    def testCreate(self):
        gr = self.I.GroupRecord(-1, self.gname, self.gname)
        self.gm.create(gr)
        self.assertRaises(self.ICore.AlreadyExistsError,
                          self.gm.create, gr)

    def testModify(self):
        gr = self.I.GroupRecord(-1, self.gname, self.gname)
        gr.gid = self.gm.create(gr)
        gr.name = "netadmins"
        self.assertRaises(self.ICore.AlreadyExistsError,
                          self.gm.modify, gr)


tests = load(excepionUserTest, exceptionGroupTest)

if __name__ == '__main__':
    main(tests)

