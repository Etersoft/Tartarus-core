#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    d = server.getZone('asdffdsa.org')
    for r in d.findRecords('xx4%',2):
        print r.type, r.data, r.name

