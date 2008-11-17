#!/usr/bin/env python
"""
Deployment Testing Script.

Here is some information on our deployment requrements:

Needed Proxies:
 *Proxy*                            *Type*
 Tartarus.deployPrx.DNSService      Tartarus::core::Service
 Tartarus.deployPrx.DNS             Tartarus::DNS::Server
 Tartarus.deployPrx.GroupManager    Tartarus::SysDB::GroupManager
 Tartarus.deployPrx.Kadmin          Tartarus::Kerberos::Kadmin
 Tartarus.deployPrx.KerberosService Tartarus::core::Service
 Tartarus.deployPrx.SysDBService    Tartarus::core::Service
 Tartarus.deployPrx.UserManager     Tartarus::SysDB::UserManager

Options
  *Name*       *Type* *Madatory*
  domainname   string M
  hostname     string M
  ip           string M
  kadmin_port  int    O
  kdc_cfg_path string O
  kdc_port     int    O
  mask         int    M
  name         string M
  password     string M

Forces: dns_force, sysdb_force, krb_force
"""

import sys, os, Ice, Tartarus

Tartarus.slices.path = ['../../slice']

from Tartarus.deploy import *

def init():
    if 'ICE_CONFIG' not in os.environ:
        sys.argv.append('--Ice.Config=./config.client')
    return Ice.initialize(sys.argv)

def make_options():
    return {
         'sysdb_force': 'True',
         'krb_force'  : 'True',
         'dns_force': 'True',
         'domainname' : 'tartarus.test.local',
         'hostname'   : 'server.tartarus.test.local',
         'ip'         : '192.168.44.2',
         'mask'       : 24,
         'name'       : 'admin',
         'password'   : 'admin' }



def main():
    variants = {
        'sysdb' : deploy_sysdb,
        'dns'   : deploy_dns,
        'krb'   : deploy_kadmin }

    def fail():
        print "Usage: %s [%s]" % (sys.argv[0],
                                  '|'.join(variants.keys()) )
        sys.exit(-1)

    if len(sys.argv) > 2:
        fail()
    comm = init()
    opts = make_options()

    if len(sys.argv) == 2:
        todo = variants.get(sys.argv[1])
        if not todo:
            fail()
        print "Deploing", sys.argv[1]
        sys.exit(todo(comm, opts))

    for name, todo in variants.iteritems():
        print "Deploing", name
        todo(comm, opts)
    sys.exit(0)


if __name__ == '__main__':
    main()

