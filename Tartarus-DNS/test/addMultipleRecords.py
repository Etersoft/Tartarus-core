#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS


def test(com, server):
    d = server.getZone('eter.ru')
    records = [
            DNS.Record(
                    name="xx%d" %num,
                    type=DNS.RecordType.A,
                    data='192.168.44.%d' % num,
                    ttl=-1, prio=-1
                    )
            for num in xrange(44,55)
            ]
    d.addRecords(records)

