#! /usr/bin/env python
# List Servers, create server, drop server by 2 different methods

import Tartarus
from Tartarus.iface import DNS

def test(com, server):
    soar = DNS.SOARecord(
            nameserver='eter.ru',
            hostmaster='nobody.eter.ru',
            serial=0,
            refresh=43200,
            retry=3600,
            expire=604800,
            ttl=3600
            )
    server.createZone('xeter.ru', soar)



