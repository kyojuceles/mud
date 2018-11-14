# Network 기능을 가진 component

from .gameobject import Component

class GocNetworkBase(Component):
    
    def __init__(self):
        pass

    def send(self, msg: str):
        raise NotImplementedError('You should implement Send method.')

class GocNetwork(GocNetworkBase):

    def __init__(self):
        pass
    
    def send(self, msg: str):
        pass

class GocNetworkPass(GocNetworkBase):   

    def __init__(self):
        pass

    def send(self, msg: str):
        pass

class NetworkConsoleEventBase:

    def on_receive(self, msg: str):
        raise NotImplementedError

class GocNetworkConsole(GocNetworkBase):
     
    def __init__(self, event: NetworkConsoleEventBase):
        assert(isinstance(event, NetworkConsoleEventBase))
        self._event = event

    def send(self, msg: str):
        self._event.on_receive(msg)