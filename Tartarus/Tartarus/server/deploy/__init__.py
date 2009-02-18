

__all__ = ['deploy_sysdb', 'deploy_kadmin', 'deploy_dns',
           'save_keys', 'client']

def deploy_sysdb(comm, opts):
    import Tartarus
    import Tartarus.deploy.SysDB
    Tartarus.deploy.SysDB.deploy_sysdb(comm, opts)


def deploy_kadmin(comm, opts):
    import Tartarus
    import Tartarus.deploy.Kadmin5
    Tartarus.deploy.Kadmin5.deploy_kadmin(comm, opts)

def deploy_dns(comm, opts):
    import Tartarus
    import Tartarus.deploy.DNS
    Tartarus.deploy.DNS.deploy_dns(comm, opts)

def save_keys(spr, keytab=None):
    import kadmin5, os

    keytab = kadmin5.keytab(keytab)

    # remove all other keys of this principal (from previous deployments?)
    try:
        keytab.remove_princ(spr.name)
    except RuntimeError, e:
        if e.args[0] != os.errno.ENOENT:
            raise
    for k in spr.keys:
        keytab.add_entry(spr.name, k.kvno, k.enctype, k.data)

