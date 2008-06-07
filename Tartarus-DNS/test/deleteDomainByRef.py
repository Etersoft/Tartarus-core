#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    d = server.getDomain('eter.ru')
    server.deleteDomainByRef(d)
    try:
        d = server.getDomain('eter.ru')
        print 'WTF'
    except DNS.Errors.ObjectNotFound:
        print 'OK'



