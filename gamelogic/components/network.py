#network.py
from gamelogic.global_instance import GlobalInstance
from .gameobject import Component
from .entity import GocEntity
from ..world.world import World
from ..world.map import Map

class GocNetworkBase(Component):
    ''' 
    client로 메시지를 보내는 기능을 담당하는 컴포넌트의 base
    '''
    def __init__(self):
        super().__init__() 

    def send(self, msg: str):
        raise NotImplementedError('You should implement Send method.')

    def broadcast_in_map(self, msg: str, is_except_owner: bool = False):
        entity: GocEntity = self.get_component(GocEntity)
        owner = self.get_owner()
        map = entity.get_map()
        if map is not None:
            objs = map.get_object_list()
            for obj in objs:
                if is_except_owner and obj == owner:
                    continue
                obj.get_component(GocNetworkBase).send(msg)

    def broadcast_in_world(self, msg: str, is_except_owner: bool = False):
        world: World = GlobalInstance.get_world()
        owner = self.get_owner()
        objs = world.get_player_list()
        for obj in objs:
            if is_except_owner and obj == owner:
                continue
            obj.get_component(GocNetworkBase).send(msg)
        
class GocNetwork(GocNetworkBase):
    ''' 
    send()를 호출하면 네트워크상으로 연결된 client에게 메시지를 보내는 컴포넌트.
    Player GameObject들이 가지게 된다.
    '''
    def __init__(self):
        pass
    
    def send(self, msg: str):
        pass

class GocNetworkPass(GocNetworkBase):   
    ''' 
    send()를 호출했을때 아무일도 하지 않는 컴포넌트. NPC GameObject들이 가지게 된다.
    '''
    def __init__(self):
        pass

    def send(self, msg: str):
        pass

class GocNetworkConsole(GocNetworkBase):
    ''' 
    send()를 호출했을때 등록된 NetworkConsoleEventBase instance로 이벤트를 전달하는 클래스
    on_receive(self, msg: str)을 호출하게 되며 Local Player GameObject가 가지게 된다.
    '''   
    def __init__(self, event):
        self._event = event

    def send(self, msg: str):
        self._event(msg)