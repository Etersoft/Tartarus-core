#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    d = server.getDomain('eter.ru')
    d.addRecord(DNS.Record(
        name='bar',
        type=DNS.RecordType.A,
        content='192.168.44.28',
        ttl=-1, prio=-1
        ))





