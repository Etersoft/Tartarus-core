import subprocess
from os import path

def get_service_script(name):
    return path.join('/etc/init.d/', name)

def get_switch_command():
    return '/sbin/chkconfig'

def service_command(service, command):
    try:
        script = get_service_script(service)
        if not path.exists(script):
            raise 'service "%s" not found' % service
        subprocess.check_call([script, command])
    except subprocess.CalledProcessError, e:
        raise 'command "%s" for service "%s" failed: %s' % (command,
                                                          service,
                                                          e.message)
def service_switch(service, state):
    try:
        command = get_switch_command()
        subprocess.check_call([script, service, state])
    except subprocess.CalledProcessError, e:
        raise 'switch state for service "%s" to "%s" failed: %s' % (service,
                                                                    state,
                                                                    e.message)
def service_start(service):
    service_command(service, 'start')

def service_stop(service):
    service_command(service, 'start')

def service_status(service):
    service_command(service, 'status')

def service_on(service):
    service_switch(service, 'on')

def service_off(service):
    service_switch(service, 'off')
