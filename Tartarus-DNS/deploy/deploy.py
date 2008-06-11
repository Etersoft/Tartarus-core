#!/usr/bin/env python

import sys, Ice, Tartarus
from Tartarus.iface.DNS import *

def connect(com):
    pr = com.propertyToProxy("Tartarus.DNS.Prx")
    if not pr:
        raise ConfigError
    server = ServerPrx.checkedCast(pr)
    return server

local_data = [
        ('localhost',
            SOARecord('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                  Record('localhost', RecordType.NS, 'localhost', -1, -1)
                , Record('localhost', RecordType.A, '127.0.0.1', -1, -1)
            ]),
        ('127.in-addr.arpa',
            SOARecord('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                  Record('127.in-addr.arpa', RecordType.NS, 'localhost', -1, -1)
                , Record('1.0.0.127.in-addr.arpa', RecordType.PTR, 'localhost', -1, -1)
                , Record('0.0.0.127.in-addr.arpa', RecordType.PTR, 'localdomain', -1, -1)
            ]),
        ('localdomain',
            SOARecord('localhost', 'root.localhost',  0, 43200, 3600, 604800, 3600),
            [
                  Record('localdomain', RecordType.NS, 'localhost')
                , Record('localdomain', RecordType.A, '127.0.0.0')
                , Record('localhost.localdomain', RecordType.CNAME, 'localhost')
            ]),
    ]

def process(server, zonedata):
    zonedata = list(zonedata)
    for name, soar, records in zonedata:
        print " zone:", name
        server.createZone(name, soar)
        zone = server.getZone(name)
        zone.addRecords(records)

def invert_ip(ip):
    delim = '.'
    l = ip.split(delim)
    if len(l) != 4:
        raise ValueError("Not an ip address", ip)
    l.reverse()
    return delim.join(l) + '.in-addr.arpa'

def reverse_record(r):
    if r.type is not RecordType.A:
        raise ValueError("Cannot reverse record of given type", r.type)
    res.type = RecordType.PTR
    res.data = r.name
    res.name = invert_ip(r.data)
    res.ttl = r.ttl
    res.prio = r.prio
    return res

def basic_zone(domain, ns, hostmaster):
    return  (domain,
                SOARecord(ns, hostmaster,  0, 43200, 3600, 604800, 3600),
                [Record(domain, RecordType.NS, ns, -1, -1)])

def _parse_options(args):
    import optparse
    usage = "usage: %prog [options and Ice options]"
    version = "%prog 0.0.1"

    parser = optparse.OptionParser(
            usage=usage,
            version=version)

    parser.add_option("-z", "--zone", action="append",
            help="add zone ZONE to serve")
    parser.add_option("-s", "--nameserver",
            help="nameserver domain name (defaults to fqdn if needed)")
    parser.add_option("-m", "--hostmaster", default="root",
            help="name of hostmaster")
    parser.add_option("--nolocal", action="store_true",
            help="do not add local zones (like 'localhost.')")
    parser.add_option("-a", "--allow-recursion", action="append",
            help="ip and mask (like 192.168.0.0/24)")
    parser.add_option("-r", "--recursor",
            help="ip address of recursor")

    opts, args = parser.parse_args(args)

    if len(args) > 1:
        raise ValueError("Positional arguments are not supported.", args[0])

    if opts.nameserver is None:
        import socket
        opts.nameserver = socket.getfqdn()

    c = opts.hostmaster.count('@')
    if c == 1:
        opts.hostmaster = opts.hostmaster.replace('@','.')
    elif c > 1:
        raise ValueError("Bad hostmaster paramter", opts.hostmaster)

    if opts.hostmaster.find('.') < 0:
        opts.hostmaster += '.' + opts.nameserver

    return opts

def inital_config(srv, opts):
    srv_opts = []
    print "creating database"
    srv.initNewDatabaseUnsafe([])
    print "processing zones"
    if not opts.nolocal:
        process(srv, local_data)
    if opts.zone:
        process(srv,
                (basic_zone(z, opts.nameserver, opts.hostmaster)
                 for z in opts.zone) )

    if opts.recursor:
        srv_opts.append(ServerOption('recursor', opts.recursor))
    if opts.allow_recursion and len(opts.allow_recursion) > 0:
        srv_opts.append(ServerOption('allow-recursion',
                        ' '.join(opts.allow_recursion)))

    srv.setOptions(srv_opts)

def main():
    class App(Ice.Application):
        def run(self, args):
            srv = connect(self.communicator())
            try:
                opts = _parse_options(args)
            except SystemExit, e:
                return e.code
            inital_config(srv, opts)


    return App().main(sys.argv)

if __name__ == '__main__':
    main()

