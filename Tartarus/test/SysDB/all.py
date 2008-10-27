#!/usr/bin/env python

import unittest, os, sys
from glob import glob

def main():
    s = unittest.TestSuite()
    for file in glob("*Test.py"):
        try:
            m, e = os.path.splitext(file)
            module = __import__(m)
            s.addTest(module.tests)
        except Exception, e:
            sys.stdout.write("Skipping %s because of exception: %s %s\n" %
                    (m, e.__class__.__name__, e.message))
    unittest.TextTestRunner().run(s)

if __name__ == '__main__':
    main()

