#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    d = server.getZone('asdffdsa.org')
    d.addRecord(DNS.Record(
        name='bar.asdffdsa.org.',
        type=DNS.RecordType.A,
        data='192.168.44.28',
        ttl=84600, prio=0
        ))





