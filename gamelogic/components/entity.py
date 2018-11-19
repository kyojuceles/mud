#entity.py
import weakref
from .gameobject import GameObject
from .gameobject import Component
from ..world.map import Map

class GocEntity(Component):
    '''
    캐릭터의 상태, 위치와 같은 정보를 나타내는 컴포넌트.
    '''
    STATUS_IDLE: int = 1
    STATUS_BATTLE: int = 2
    STATUS_DEATH: int = 3

    def __init__(self):
        super().__init__() 
        self._map = None
        self._target = None
        self._status = GocEntity.STATUS_IDLE
        self._is_try_flee = False
        self._destroy = False

    def get_status(self):
        return self._status

    def set_status(self, status: int):
        self._status = status

    def set_map(self, map: Map):
        if map is None:
            self._map = None
        else:
            assert(isinstance(map, Map))
            self._map = weakref.ref(map)

    def destroy(self):
        self._destroy = True

    def get_map(self) -> Map:
        if self._map is None:
            return None
        
        return self._map()

    def set_target(self, target: GameObject):
        if target is None:
            self._target = None
        else:
            assert(isinstance(target, GameObject))
            self._target = weakref.ref(target)

    def get_target(self) -> GameObject:
        if self._target is None:
            return None

        return self._target()

    def get_status_desc(self) -> str:
        desc = ''

        if self._status == GocEntity.STATUS_DEATH:
            desc = self.get_owner_name_title() + '의 시체가 놓여있습니다.\n'
        elif self._status == GocEntity.STATUS_BATTLE and \
             self.get_target() is not None:
            desc = self.get_owner_name_title() + '이 ' + \
            self.get_target().get_name_title() + \
            '를 공격중입니다.\n'
        else:
            desc = self.get_owner_name_title() + '이 서 있습니다.\n'

        return desc

    def is_try_flee(self) -> bool:
        return self._is_try_flee

    def try_flee(self):
        self._is_try_flee = True

    def reset_flee(self):
        self._is_try_flee = False

    def is_die(self) -> bool:
        return self._status == GocEntity.STATUS_DEATH

    def is_battle(self) -> bool:
        return self._status == GocEntity.STATUS_BATTLE

    def is_idle(self) -> bool:
        return self._status == GocEntity.STATUS_IDLE

    def is_destroy(self) -> bool:
        return self._destroy
    