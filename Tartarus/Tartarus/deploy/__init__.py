

__all__ = ['deploy_sysdb', 'deploy_kadmin', 'deploy_dns']

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

