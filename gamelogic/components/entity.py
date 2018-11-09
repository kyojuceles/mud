import weakref

from .gameobject import Component
from ..utils import instance_checker

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

    def get_desc(self):
        return '[' + self.get_owner_name() +']님이 서 있습니다.\n'
    