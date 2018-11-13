# Network 기능을 가진 component

from .gameobject import Component

class GocNetworkBase(Component):
    name = 'GocNetworkBase'
    
    def __init__(self):
        pass

    def send(self, msg):
        raise NotImplementedError('You should implement Send method.')

class GocNetwork(GocNetworkBase):

    def __init__(self):
        pass
    
    def send(self, msg):
        pass

class GocNetworkPass(GocNetworkBase):   

    def __init__(self):
        pass

    def send(self, msg):
        pass

class NetworkConsoleEventBase:

    def on_receive(self, msg):
        raise NotImplementedError

class GocNetworkConsole(GocNetworkBase):
     
    def __init__(self, event):
        assert(isinstance(event, NetworkConsoleEventBase))
        self._event = event

    def send(self, msg):
        self._event.on_receive(msg)