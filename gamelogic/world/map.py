# map.py

import weakref
from ..utils import instance_checker

class Map:
    
    def __init__(self, id, name = '', desc = ''):
        self._id = id
        self._visitable_maps = weakref.WeakValueDictionary()
        self._name = name
        self._desc = desc

    def get_id(self):
        return self._id
        
    def get_name(self):
        return self._name
    
    def get_desc(self):
        return self._desc

    def add_visitable_map(self, dest, map):
        assert(instance_checker.is_map(map))
        if dest in self._visitable_maps:
            return False

        self._visitable_maps[dest] = map
        return True

    def get_visitable_map(self, dest):
        if dest not in self._visitable_maps:
            return None

        return self._visitable_maps[dest]

    def get_visitable_map_list(self):
        return [(item[0], item[1].get_id()) for item in self._visitable_maps.items()]
            
    def update(self):
        pass
    