
import os

def backup_file(filename):
    """If file exists, try to rename it.

    New name is oldame + '.' + counter, where counter is minimal positive
    integer, such that file with that name does not exist.
    """
    exists = os.path.exists
    if not exists(filename):
        return
    i = 1
    while exists(filename + '.' + str(i)):
        i += 1
    os.rename(filename, filename + '.' + str(i))


def gen_config(config_name, config_template, opts=None, backup=False):
    if opts is None:
        opts = {}
    if backup:
        backup_file(config_name)
    open(config_name,'w').write(config_template % opts)



def gen_config_from_file(config_name, template_file_name,
                         opts=None, backup=False):
    gen_config(config_name, open(template_file_name).read(), opts, backup)

