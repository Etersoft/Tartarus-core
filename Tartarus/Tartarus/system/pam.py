import subprocess
from os import path

def get_control_command():
    return 'control'

def control_command(facility, status):
    try:
        command = get_control_command()
        subprocess.check_call([command, facility, status])
    except subprocess.CalledProcessError, e:
        raise 'facility "%s" with status "%s" failed: %s' % (facility,
                                                             status,
                                                             e.message)
def set_system_auth(status):
    control_command('system-auth', status)

def set_tartarus_auth():
    set_system_auth('tartarus')

def set_local_auth():
    set_system_auth('local')
