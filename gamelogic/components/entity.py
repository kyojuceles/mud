import weakref

from .gameobject import Component
from gamelogic.utils import instance_checker

class GocEntity(Component):
    name = 'GocEntity'

    def __init__(self):
        self.map = None

    def set_map(self, map):
        assert(instance_checker.is_map(map))
        self.map = weakref.ref(map)

    def get_map(self):
        if self.map is None:
            return None
        
        return self.map()
    