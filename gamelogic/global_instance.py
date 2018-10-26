# GameLogic내에서 사용되는 글로벌 instance를 리턴하는 클래스
class GlobalInstance:
    __global_instance_container = None

    @classmethod
    def set_global_instance_container(cls, ins):
        assert(isinstance(ins, GlobalInstanceContainer))
        cls.__global_instance_container = ins

    @classmethod
    def get_event(cls):
        return cls.__global_instance_container.get_event()

    @classmethod
    def get_world(cls):
        return cls.__global_instance_container.get_world()

'''
GameLogicProcessorEvent와 World를 포함하는 클래스의 부모. 다음의 구현이 필요하다.
1. __init__에서 GlobalInstance.set_global_instance_container(self)를 호출
2. get_event()를 구현하고 GameLogicProcessorEvent의 instance를 리턴해줘야 한다.
3. get_world()를 구현하고 World의 instance를 리턴해줘야 한다.
'''
class GlobalInstanceContainer:

    def get_event(self):
        raise NotImplementedError

    def get_world(self):
        raise NotImplementedError

#Game Logic의 이벤트를 받아오는 클래스
class GameLogicProcessorEvent:
    
    def event_output(self, output):
        raise NotImplementedError
        