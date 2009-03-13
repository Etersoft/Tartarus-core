def init(adapter):
    props = adapter.getCommunicator().getProperties()
    options.init(props)
    Config.get().load()
    network.init(adapter)

def shutdown():
    r = Runner.get()
    if r.status() == Status.RUN:
        r.stop()

import options
from config import Config
import network
from runner import Runner, Status

