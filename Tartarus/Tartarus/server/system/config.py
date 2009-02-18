from __future__ import with_statement

import os, re
from contextlib import contextmanager


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



# libshell-like configuration file management

def config_get(lines, param, delim="="):
    expr = re.compile("^\s*%s%s(.*)$"
                      % (re.escape(param), delim))
    gen = (expr.match(l) for l in lines)
    return (e.group(1) for e in gen if e)

def config_get_file(filename, param, delim="="):
    with open(filename) as f:
        return list(config_get(f, param, delim))


def config_get_first(lines, param, delim="="):
    for i in config_get(lines, param, delim):
        return i
    return None

def config_get_first_file(filename, param, delim="="):
    with open(filename) as f:
        return config_get_first(f, param, delim)


def config_comment_filter(lines, param, delim="=", comment="# "):
    expr = re.compile("^\s*%s%s(.*)$"
                      % (re.escape(param), delim))
    for l in lines:
        if expr.match(l):
            yield comment + l
        else:
            yield l

def config_del_filter(lines, param, delim="="):
    expr = re.compile("^\s*%s%s(.*)$"
                      % (re.escape(param), delim))
    return (l for l in lines if not expr.match(l))

def config_add_filter(lines, param, value, w_delim="="):
    for l in lines:
        yield l
    if isinstance(value, basestring):
        yield param + w_delim + value + '\n'
    else:
        for i in value:
            yield param + w_delim + i + '\n'

def config_set_filter(lines, param, value, r_delim="=", w_delim="="):
    return config_add_filter(
            config_del_filter(lines, param, r_delim),
            param, value, w_delim)


@contextmanager
def file_to_filter(filename, backup=False):
    i = open(filename)
    if backup:
        backup_file(filename)
    else:
        os.unlink(filename)
    o = open(filename, 'w')
    yield i, o
    i.close()
    o.close()

def _filter2file(func):
    def wrapper(filename, *args, **kwargs):
        with file_to_filter(filename, kwargs.get('backup')) as (i, o):
            if 'backup' in kwargs:
                del kwargs['backup']
            for l in func(i, *args, **kwargs):
                o.write(l)
    wrapper.__name__ = func.__name__.rpartition('_')[0] + '_file'
    wrapper.__doc__ = func.__doc__
    return wrapper

# pylint: disable-msg=C0103
config_comment_file = _filter2file(config_comment_filter)
config_del_file = _filter2file(config_del_filter)
config_set_file = _filter2file(config_set_filter)


