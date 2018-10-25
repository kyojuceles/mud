from .utils import instance_checker
from .world.world import World

#Game Logic의 이벤트를 받아오는 클래스
class GameLogicProcessorEvent:
    
    def event_output(self, output):
        raise NotImplementedError
        
'''
Game Logic을 처리하는 클래스

1. 입력을 받아서 처리하고 결과를 이벤트 클래스에 알려준다.
2. GameLogicProcessor.get_instance()로 글로벌 instance를 얻을 수 있다.
'''
class GameLogicProcessor:
    __global_instance = None
     
    def __init__(self, event):
        self._event = event
        self._is_start = False
        self._world = World()
        self._set_global_instance(self)

    def start(self):
        self._is_start = True
        self.get_event_instance().event_output('서버를 시작합니다')
    
    def stop(self):
        self._is_start = False
        self.get_event_instance().event_output('서버를 종료합니다')

    def update(self):
        if not self._is_start:
            return

        self._world.update()

    def process(self, cmd):
        pass
    
    @classmethod
    def get_instance(cls):
        return cls.__global_instance

    @classmethod
    def get_event_instance(cls):
        return cls.get_instance()._event

    @classmethod
    def get_world(cls):
        return cls.get_instance()._world

    @classmethod
    def _set_global_instance(cls, instance):
        cls.__global_instance = instance
