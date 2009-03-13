#!/usr/bin/env python

from testbase import *

class underscoreTest(TestWithUser):
    def runTest(self):
        name = self.name
        self.name += '_WITH_UNDERSCORE'
        ur = self.I.UserRecord(-1, self.gid, self.name, self.name)
        id = self.um.create(ur)
        users = self.um.search(name + '_', -1)
        self.assert_(len(users) > 0)
        self.um.delete(id)


tests = load(underscoreTest)

if __name__ == '__main__':
    main(tests)

