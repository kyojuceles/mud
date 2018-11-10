import weakref

from .gameobject import Component
from ..utils import instance_checker

class GocEntity(Component):
    name = 'GocEntity'

    STATUS_IDLE = 1
    STATUS_BATTLE = 2
    STATUS_DEATH = 3

    def __init__(self):
        self._map = None
        self._target = None
        self._status = GocEntity.STATUS_IDLE

    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status

    def set_map(self, map):
        assert(instance_checker.is_map(map))
        self._map = weakref.ref(map)

    def get_map(self):
        if self._map is None:
            return None
        
        return self._map()

    def set_target(self, target):
        assert(instance_checker.is_gameobject(target))
        self._target = weakref.ref(target)

    def get_target(self):
        if self._map is None:
            return None

        return self._target()

    def get_desc(self):
        desc = ''

        if self._status == GocEntity.STATUS_DEATH:
            desc = self._make_name_title() + '의 시체가 놓여있습니다.\n'
        elif self._status == GocEntity.STATUS_BATTLE and \
             self.get_target() is not None:
            desc = self._make_name_title() + '이 ' + \
            self.get_target().get_component('GocEntity')._make_name_title() + \
            '를 공격중입니다.\n'
        else:
            desc = self._make_name_title() + '이 서 있습니다.\n'

        return desc

    def _make_name_title(self):
        return '[' + self.get_owner_name() + ']'
    