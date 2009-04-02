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

