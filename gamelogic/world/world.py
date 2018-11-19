#world.py

import gamelogic.global_define as global_define
from ..components.gameobject import GameObject
from ..components.updater_base import GocUpdaterBase
from .map import Map

class World:
    '''
    map, obj를 관리하는 클래스
    '''
    def __init__(self):
        self._maps = {}
        self._players = {}
        self._objs = []
        self._update_tick_count = 0

    def add_player(self, player: GameObject) -> bool:
        assert(isinstance(player, GameObject))

        if player.get_name() in self._players:
            return False
        
        self._players[player.get_name()] = player
        assert(self._add_object(player))
        return True

    def del_player(self, player: GameObject) -> bool:
        assert(isinstance(player, GameObject))

        if player.get_name() not in self._players:
            return False

        del self._players[player.get_name()]
        self._del_object(player)
        return True

    def get_player(self, name: str) -> GameObject:
        if name not in self._players:
            return None

        return self._players[name]

    def get_player_list(self) -> GameObject:
        return list(self._players.values())

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

        #회복턴이 되었는지 체크
        is_recovery_tick: bool = False
        self._update_tick_count += 1
        if self._update_tick_count >= global_define.TICK_FOR_UPDATE_RECOVERY:
            self._update_tick_count = 0
            is_recovery_tick = True

        #오브젝트들의 update를 실행
        for obj in self._objs:
            updater: GocUpdaterBase = obj.get_component(GocUpdaterBase)
            if updater is not None:
                updater.update()
                if is_recovery_tick:
                    updater.update_recovery()




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
