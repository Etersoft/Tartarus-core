#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    server.deleteZone('asdffdsa.org')
    try:
        d = server.getZone('asdffdsa.org')
        print 'WTF'
    except DNS.ObjectNotFound:
        print 'OK'



