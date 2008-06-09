#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    d = server.getZone('xeter.ru')
    server.deleteZoneByRef(d)
    try:
        d = server.getZone('xeter.ru')
        print 'WTF'
    except DNS.ObjectNotFound:
        print 'OK'



