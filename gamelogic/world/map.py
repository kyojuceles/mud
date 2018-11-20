# map.py

from __future__ import annotations
import weakref
from typing import List, Optional
from ..components.gameobject import GameObject

class Map:
    """
    방 하나를 담당하는 클래스
    """
    
    def __init__(self, id: str, name: str = '', desc: str = ''):
        self._id = id
        self._visitable_maps = weakref.WeakValueDictionary()
        self._name = name
        self._desc = desc
        self._objs = []

    def get_id(self) -> str:
        return self._id
        
    def get_name(self) -> str:
        return self._name
    
    def get_desc(self) -> str:
        output_string = '[' + self.get_name() + ']'
        output_string += '\n'
        output_string += self._desc
        output_string += '\n'

        visitable_map = self._visitable_maps.keys()
        output_string += '['
        output_string += '.'.join(visitable_map)
        output_string += ']\n'

        return output_string

    def add_visitable_map(self, dest: str, map: Map) -> bool:
        assert(isinstance(map, Map))
        if dest in self._visitable_maps:
            return False

        self._visitable_maps[dest] = map
        return True

    def get_visitable_map(self, dest: str):
        if dest not in self._visitable_maps:
            return None

        return self._visitable_maps[dest]

    def get_visitable_map_list(self) -> List[Optional[tuple]]:
        return [(item[0], item[1].get_id()) for item in self._visitable_maps.items()]

    def get_visitable_map_dest_list(self) -> List[Optional[str]]:
        return list(self._visitable_maps.keys())
            
    def update(self):
        pass

    def enter_map(self, obj: GameObject) -> bool:
        if obj in self._objs:
            return False

        self._objs.append(obj)
        self._objs.sort(key = lambda obj : obj.get_name())
        return True

    def leave_map(self, obj: GameObject) -> bool:
        if obj not in self._objs:
            return False

        self._objs.remove(obj)
        self._objs.sort(key = lambda obj : obj.get_name())
        return True

    def broadcast(self, msg: str):
        from ..components.network import GocNetworkBase
        for obj in self._objs:
            network_base: GocNetworkBase = obj.get_component(GocNetworkBase)
            network_base.send(msg)

    def get_object(self, name: str) -> GameObject:
        '''
        이름으로 오브젝트를 얻어온다.
        만약 앞에 숫자. 형태가 나오면 숫자 순서에 있는 오브젝트를 얻어온다.
        예) '1.병사' -> 첫번째 '병사', '2.병사' -> 두번째 '병사'
        '''
        words = name.split('.')
        order = 0
        key = name
        if len(words) > 1 and words[0].isdigit():
            order = int(words[0]) - 1
            key = words[1]

        obj_list = [obj for obj in self._objs if obj.get_name() == key]
        if order >= len(obj_list):
            return None
        
        return obj_list[order]

    def get_object_list(self) -> List[Optional[GameObject]]:
        return tuple(self._objs)



        


    

    