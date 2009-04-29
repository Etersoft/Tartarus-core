from Tartarus.system import Error
import subprocess
from os import path

class ServiceNotFound(Error):
    pass

def get_service_script(name):
    script = path.join('/etc/init.d/', name)
    if not path.exists(script):
        raise ServiceNotFound('service "%s" not found' % name)
    return script

def get_switch_command():
    # Check for service exists
    get_service_script(service)
    return 'chkconfig'

def service_command(service, command):
    try:
        script = get_service_script(service)
        subprocess.check_call([script, command])
    except subprocess.CalledProcessError, e:
        raise Error('command "%s" for service "%s" failed: %s'
                    % (command, service, e.message))


def service_switch(service, state):
    try:
        command = get_switch_command()
        subprocess.check_call([command, service, state])
    except subprocess.CalledProcessError, e:
        raise Error('switch state for service "%s" to "%s" failed: %s'
                    % (service, state, e.message))


def tartarus_start_deploy():
    service_command('Tartarus', 'deploy')

def service_start(service):
    service_command(service, 'start')

def service_restart(service):
    service_command(service, 'restart')

def service_stop(service):
    service_command(service, 'stop')

def service_status(service):
    service_command(service, 'status')

def service_on(service):
    service_switch(service, 'on')

def service_off(service):
    service_switch(service, 'off')

