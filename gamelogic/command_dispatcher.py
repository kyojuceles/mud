#command_dispatcher.py
from .processor import GameLogicProcessor
from gamelogic.world.world import World
from gamelogic.world.map import Map
from gamelogic.components import factory

class CommandDispatcher:

    def __init__(self, processor):
        assert(isinstance(processor, GameLogicProcessor))
        self._processor = processor
        self._player = None

    def init_test(self):
        world = self._processor.get_world()
        map1 = Map('광장_00_00')
        map2 = Map('광장_00_01')
        map3 = Map('광장_00_02')

        map1.add_visitable_map('남', map2)
        map1.add_visitable_map('북', map3)

        map2.add_visitable_map('북', map1)
        map3.add_visitable_map('남', map1)

        world.add_map(map1)
        world.add_map(map2)
        world.add_map(map3)

    def get_player(self, index):
        return self._player

    def dispatch(self, index, cmd):
        if cmd == '종료':
            return False

        if cmd == '접속':
            player = factory.create_object('플레이어', 100, 10, 1, 1)
            world = self._processor.get_world()
            world.add_player(player)
            self._player = player
            return True

        if cmd in ['남', '북']:
            if self._player is not None:
                behaviour = self._player.get_component('GocBehaviour')
                behaviour.visit_map(cmd)
            return True

        GameLogicProcessor.get_event_instance().event_output('명령어가 존재하지 않습니다.')        
        return True