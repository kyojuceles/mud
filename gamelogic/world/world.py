#world.py

from ..components.gameobject import GameObject
from ..components.updater_base import GocUpdaterBase
from .map import Map

'''
map, obj를 관리하는 클래스
'''
class World:

    def __init__(self):
        self._maps = {}
        self._players = {}
        self._objs = []

    def add_player(self, player: GameObject) -> bool:
        assert(isinstance(player, GameObject))

        if player.get_name() in self._players:
            return False
        
        self._players[player.get_name()] = player
        assert(self._add_object(player))
        return True

    def get_player(self, name: str) -> GameObject:
        if name not in self._players:
            return None

        return self._players[name]

    def add_npc(self, npc: GameObject):
        assert(isinstance(npc, GameObject))
        assert(self._add_object(npc))
        
    def add_map(self, map: Map) -> bool:
        assert(isinstance(map, Map))

        if map.get_id() in self._maps:
            return False

        self._maps[map.get_id()] = map
        return True

    def get_map(self, id: str) -> Map:
        if id not in self._maps:
            return None

        return self._maps[id]

    def update(self):
        for map in self._maps.values():
            map.update()

        for obj in self._objs:
            updater: GocUpdaterBase = obj.get_component(GocUpdaterBase)
            if updater is not None:
                updater.update()

    def _add_object(self, obj: GameObject) -> bool:
        if obj in self._objs:
            return False

        self._objs.append(obj)
        return True

    def _del_object(self, obj: GameObject) -> bool:
        if obj not in self._objs:
            return False

        self._objs.remove(obj)
        return True
