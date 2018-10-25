#world.py

from ..utils import instance_checker

'''
map, obj를 관리하는 클래스
'''
class World:

    def __init__(self):
        self._maps = {}
        self._players = {}
        self._objs = []

    def add_player(self, player):
        assert(instance_checker.is_player(player))

        if player.name in self._players:
            return False
        
        self._players[player.name] = player
        assert(self._add_object(player))
        return True

    def get_player(self, name):
        if name not in self._players:
            return None

        return self._players[name]

    def add_npc(self, npc):
        assert(instance_checker.is_npc(npc))
        assert(self._add_object(npc))
        
    def add_map(self, map):
        assert(instance_checker.is_map(map))

        if map.get_id() in self._maps:
            return False

        self._maps[map.get_id()] = map
        return True

    def get_map(self, id):
        if id not in self._maps:
            return None

        return self._maps[id]

    def update(self):
        for map in self._maps:
            map.update()

        for obj in self._objs:
            updater = obj.get_component('GocUpdater')
            if updater is not None:
                updater.update()

    def _add_object(self, obj):
        if obj in self._objs:
            return False

        self._objs.append(obj)
        return True

    def _del_object(self, obj):
        if obj not in self._objs:
            return False

        self._objs.remove(obj)
        return True
