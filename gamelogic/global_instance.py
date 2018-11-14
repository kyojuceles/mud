#global_instance.py
from __future__ import annotations

class GlobalInstance:
    '''
    GameLogic내에서 사용되는 글로벌 instance를 리턴하는 클래스
    '''
    __global_instance_container: 'GlobalInstanceContainer' = None

    @classmethod
    def set_global_instance_container(cls, ins: 'GlobalInstanceContainer'):
        assert(isinstance(ins, GlobalInstanceContainer))
        cls.__global_instance_container = ins

    @classmethod
    def get_event(cls) -> 'GameLogicProcessorEvent':
        return cls.__global_instance_container.get_event()

    @classmethod
    def get_world(cls) -> 'World':
        return cls.__global_instance_container.get_world()


class GlobalInstanceContainer:
    '''
    GameLogicProcessorEvent와 World를 포함하는 클래스의 부모. 다음의 구현이 필요하다.
    1. __init__에서 GlobalInstance.set_global_instance_container(self)를 호출
    2. get_event()를 구현하고 GameLogicProcessorEvent의 instance를 리턴해줘야 한다.
    3. get_world()를 구현하고 World의 instance를 리턴해줘야 한다.
    '''
    def get_event(self):
        raise NotImplementedError

    def get_world(self):
        raise NotImplementedError

class GameLogicProcessorEvent:
    '''
    Game Logic의 이벤트를 받아오는 클래스
    '''
    def event_output(self, output: str):
        raise NotImplementedError
        