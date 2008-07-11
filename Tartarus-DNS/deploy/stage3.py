#!/usr/bin/env python

from __future__ import with_statement
import sys, Ice, Tartarus
import Tartarus.iface.DNS as I
from Tartarus import logging

def _strip_prefix(prefix, d):
    l = len(prefix)
    gen = ( (key[l:], val)
            for key, val in d.iteritems()
            if key.startswith(prefix) )
    return dict(gen)


def connect(com):
    try:
        pr = com.propertyToProxy("Tartarus.DNS.Prx")
        server = I.ServerPrx.checkedCast(pr)
    except Exception:
        raise I.ConfigError("Don't know how to connect DNS configurator",
                "Tartarus.DNS.Prx")
    return server


local_data = [
        ('localhost',
            I.SOARecord('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                  I.Record('localhost', I.RecordType.NS, 'localhost', -1, -1)
                , I.Record('localhost', I.RecordType.A, '127.0.0.1', -1, -1)
            ]),
        ('127.in-addr.arpa',
            I.SOARecord('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                  I.Record('127.in-addr.arpa', I.RecordType.NS, 'localhost', -1, -1)
                , I.Record('1.0.0.127.in-addr.arpa', I.RecordType.PTR, 'localhost', -1, -1)
                , I.Record('0.0.0.127.in-addr.arpa', I.RecordType.PTR, 'localdomain', -1, -1)
            ]),
        ('localdomain',
            I.SOARecord('localhost', 'root.localhost',  0, 43200, 3600, 604800, 3600),
            [
                  I.Record('localdomain', I.RecordType.NS, 'localhost')
                , I.Record('localdomain', I.RecordType.A, '127.0.0.0')
                , I.Record('localhost.localdomain', I.RecordType.CNAME, 'localhost')
            ]),
    ]


broadcast_data = [
        ('0.in-addr.arpa',
            I.SOARecord('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                I.Record('127.in-addr.arpa', I.RecordType.NS, 'localhost', -1, -1)
            ]),
        ('255.in-addr.arpa',
            I.SOARecord('localhost', 'root.localhost', 0, 43200, 3600, 604800, 3600),
            [
                I.Record('127.in-addr.arpa', I.RecordType.NS, 'localhost', -1, -1)
            ])
    ]


def process(server, zonedata, trace):
    zonedata = list(zonedata)
    for name, soar, records in zonedata:
        logging.trace('DNS', "Creating zone %s" % name, trace)
        server.createZone(name, soar)
        zone = server.getZone(name)
        zone.addRecords(records)


def mask2octets(mask):
    if mask < 8 or mask >= 32:
        raise I.ConfigError("Wrong network mask", str(mask))
    if mask == 8:
        return 1
    if 8 < mask <= 16:
        return 2
    else:
        return 3

def reverse_zone_name(a,m):
    o = mask2octets(int(m))
    a = a.split('.')
    a = a[:o]
    a.reverse()
    return '.'.join(a) + '.in-addr.arpa'


_needed_opts = [
        'DNS.ConfigFile',
        'DNS.DaemonType',
        'DNS.Hostmaster',
        'DNS.NameServer',
        'DNS.ReverseZone',
        'Domain',
        'ServerFQDN',
        'ServerIP',
        'Subnet',
        'trace'
        ]

def update_and_check_options(opts):
    if 'Domain' not in opts:
        raise I.ConfigError("Option not specified", "Domain")

    if 'ServerFQDN' not in opts:
        import socket
        opts['DNS.ServerFQDN'] = socket.getfqdn()

    if 'DNS.NameServer' not in opts:
        opts['DNS.NameServer'] = 'ns.' + opts['Domain']

    try:
        s,m = opts['Subnet'].split('/')
        m = int(m)
    except KeyError:
        raise I.ConfigError("Option not specified", 'Subnet')
    except ValueError:
        raise I.ConfigError("Invalid domain subnet", opts['Subnet'])

    if 'DNS.ReverseZone' not in opts:
        b = mask2octets(m)
        if b*8 != m:
            I.ConfigError("For your subnet, supply DNS.ReverseZone",
                    opts['Subnet'])
        opts['DNS.ReverseZone'] = reverse_zone_name(s,m)

    # DNS.Hostmaster
    if 'DNS.Hostmaster' in opts:
        c = opts['DNS.Hostmaster'].count('@')
        if c == 1:
            opts['DNS.Hostmaster'] = opts['DNS.Hostmaster'].replace('@','.')
        elif c > 1:
            raise ValueError("Bad DNS.Hostmaster paramter", opts['DNS.Hostmaster'])

        if opts['DNS.Hostmaster'].find('.') < 0:
            opts['DNS.Hostmaster'] += '.' + opts['DNS.NameServer']
    else:
        opts['DNS.Hostmaster'] = 'root.' + opts['DNS.NameServer']

    for n in _needed_opts:
        if n not in opts:
            raise I.ConfigError("Option not specified", n)

    return opts


def _ptr_record(ip, fqdn, zone):
    """Make PTR record from ip, host fqdn and reverse zone name.

    zone is in form of [[b.]c.]d.in-addr.arpa (without a terminating dot)
    """
    octets = ip.split('.')
    octets.reverse()
    if len(octets) != 4:
        raise I.ConfigError('Invalud IPv4 adress', ip)

    n = zone.count('.')
    if n < 2:
        raise I.ConfigError('Invalid reverse zone name', zone)
    elif n > 4:
        name =  octets[0] + '.'
    else:
        name = '.'.join(octets[:(5-n)]) + '.'

    return I.Record(name + zone, I.RecordType.PTR, fqdn, -1, -1)


def deploy(srv, opts):

    if opts.get('DNS.AddLocalZones', True):
        process(srv, local_data, opts['trace'])
    if opts.get('DNS.AddBroadcastZones', True):
        process(srv, broadcast_data, opts['trace'])

    domain = opts['Domain']
    ns = opts['DNS.NameServer']
    ip = opts['ServerIP']
    fqdn = opts['ServerFQDN']
    logging.trace('DNS',
            'Creating zone for domain %s' % domain,
            opts['trace'])
    z = srv.createZone(domain,
            I.SOARecord(ns, opts['DNS.Hostmaster'],
                0, 43200, 3600, 604800, 3600))
    records = [
          I.Record(domain, I.RecordType.NS, ns, -1, -1)
        , I.Record(domain, I.RecordType.A, ip, -1, -1)
        ]
    if fqdn != domain:
        records.append(I.Record(fqdn, I.RecordType.A, ip))
    if ns != domain and ns != fqdn:
        records.append(I.Record(ns, I.RecordType.CNAME, fqdn))
    z.addRecords(records)

    rzone = opts.get('DNS.ReverseZone')
    if rzone:
        logging.trace('DNS', 'Creating reverse zone', opts['trace'])
        z = srv.createZone(rzone,
            I.SOARecord(ns, opts['DNS.Hostmaster'],
                0, 43200, 3600, 604800, 3600))
        records = [
                  I.Record(rzone, I.RecordType.NS, ns, -1, -1)
                , _ptr_record(ip, fqdn, rzone)
                ]
        z.addRecords(records)

    srv_opts = []
    if 'DNS.Recursor' in opts:
        srv_opts.append(I.ServerOption('recursor', opts['DNS.Recursor']))
        srv_opts.append(I.ServerOption('allow-recursion', opts['Subnet']))
    srv.setOptions(srv_opts)


def main():
    class App(Ice.Application):
        def run(self, args):
            try:
                props = self.communicator().getProperties()
                opts = props.getPropertiesForPrefix('Deploy.')
                opts = _strip_prefix('Deploy.', opts)
                update_and_check_options(opts)
                srv = connect(self.communicator())
                deploy(srv, opts)
                return 0
            except I.ConfigError, e:
                logging.error('DNS: %s: %s' % (e.message, e.property))
                return -1
            except I.Error, e:
                logging.error('DNS: ' + e.message)
                return -1

    return App().main(sys.argv)


if __name__ == '__main__':
    main()

