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

    def add_object(self, obj: GameObject, is_player: bool) -> bool:
        assert(isinstance(obj, GameObject))

        if is_player:
            if obj.get_name() in self._players:
                return False
            self._players[obj.get_name()] = obj
            
        assert(self._add_object(obj))
        return True

    def del_object(self, obj: GameObject, is_player: bool):
        assert(isinstance(obj, GameObject))

        if is_player:
            if obj.get_name() not in self._players:
                del self._players[obj.get_name()]

        self._del_object(obj)
        return True

    def get_player(self, name: str) -> GameObject:
        if name not in self._players:
            return None

        return self._players[name]

    def get_player_list(self) -> GameObject:
        return list(self._players.values())

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

    async def update(self):
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
                await updater.update()
                if is_recovery_tick:
                    updater.update_recovery()
        
        if is_recovery_tick:
            self.respawn_npcs()

    def respawn_npcs(self): 
        from ..components import factory
        from ..components.behaviour import GocBehaviour
        for map in self._maps.values(): #type: Map
            respawn_npc_info_list = map.get_respawn_info_list()
            for info in respawn_npc_info_list: #type: RespawnInfo
                for _ in range(0, info.num):
                    obj = factory.create_object_npc(info.id)
                    behaviour: GocBehaviour = obj.get_component(GocBehaviour)
                    self.add_object(obj, False)
                    behaviour.enter_map(map.get_id())

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
