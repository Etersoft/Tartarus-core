def init(adapter):
    props = adapter.getCommunicator().getProperties()
    options.init(props)
    Config.get().load()
    network.init(adapter)

import options
from config import Config
import network

