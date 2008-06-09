#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    d = server.getZone('eter.ru')
    for r in d.getRecords(3,1):
        print r.type, r.data, r.name

