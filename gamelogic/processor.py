from .global_instance import GlobalInstance
from .global_instance import GlobalInstanceContainer
from .global_instance import GameLogicProcessorEvent
from .command_dispatcher import CommandDispatcher
from .utils import instance_checker
from .world.world import World
from .world.map import Map

'''
Game Logic을 처리하는 클래스

1. 입력을 받아서 처리하고 결과를 이벤트 클래스에 알려준다.
2. GameLogicProcessor.get_instance()로 글로벌 instance를 얻을 수 있다.
'''
class GameLogicProcessor(GlobalInstanceContainer):
    LOCAL_PLAYER_ID = 0
     
    def __init__(self, event):
        assert(isinstance(event, GameLogicProcessorEvent))
        self._is_start = False
        self._event = event
        self._world = World()
        self._command_dispatcher = CommandDispatcher()
        self._latest_player_id = GameLogicProcessor.LOCAL_PLAYER_ID
        GlobalInstance.set_global_instance_container(self)

    def init_test(self):
        map1 = Map('광장_00_00')
        map2 = Map('광장_00_01')
        map3 = Map('광장_00_02')

        map1.add_visitable_map('남', map2)
        map1.add_visitable_map('북', map3)

        map2.add_visitable_map('북', map1)
        map3.add_visitable_map('남', map1)

        self._world.add_map(map1)
        self._world.add_map(map2)
        self._world.add_map(map3)


    def start(self):
        self._is_start = True
        GlobalInstance.get_event().event_output('서버를 시작합니다')
    
    def stop(self):
        self._is_start = False
        GlobalInstance.get_event().event_output('서버를 종료합니다')

    def update(self):
        if not self._is_start:
            return

        self._world.update()

    def process(self, cmd):
        pass

    def add_player(self, name):
        return 0

    def get_event(self):
        return self._event

    def get_world(self):
        return self._world
