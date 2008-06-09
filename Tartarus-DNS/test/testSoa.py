#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    d = server.getZone('eter.ru')
    soar = DNS.SOARecord(
            nameserver='eter.ru',
            hostmaster='nobody.eter.ru',
            serial=0,
            refresh=43200,
            retry=3600,
            expire=604800,
            ttl=3600
            )

    d.setSOA(soar)
    soar.hostmaster='root.eter.ru'
    d.setSOA(soar)
    print d.getSOA()

