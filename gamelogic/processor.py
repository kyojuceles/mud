from .global_instance import GlobalInstance
from .global_instance import GlobalInstanceContainer
from .global_instance import GameLogicProcessorEvent
from .utils import instance_checker
from .world.world import World
from .world.map import Map
from .components import factory
from .components.behaviour import GocBehaviour

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
        self._latest_player_id = GameLogicProcessor.LOCAL_PLAYER_ID
        self._parser = Parser()
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

    def add_player(self, player):
        return self._world.add_player(player)

    def get_event(self):
        return self._event

    def get_world(self):
        return self._world
    
    def dispatch_msg_before_login(self, id, msg):
        pass

    def dispatch_msg_after_login(self, player, msg):
        ret, cmd, args = self._parser._cmd_parse(msg)

    def enter_map(self, player, map_id):
        assert(instance_checker.is_player(player))
        return player.get_component('GocBehaviour').enter_map(map_id)

    def move_map(self, player, dest):
        assert(instance_checker.is_player(player))
        behaviour = player.get_component('GocBehaviour')
        behaviour.move_map(dest)

class Parser:
    arg_infos_list = {}

    def _cmd_parse(self, msg):
        """
        입력받은 msg 파싱해서 형식에 맞는 cmd와 args를 리턴한다.
        input_string이 적절하지 않으면 False를 리턴한다.
        """
        assert(isinstance(msg, str))

        cmd, result_string = self._pop_word(msg)

        if cmd == '':
            return False, '', ()
 
        arg_infos = []
        if cmd in self.arg_infos_list:
            arg_infos = self.arg_infos_list[cmd]

        ret, args = self._arg_parse(result_string, arg_infos)
        return ret, cmd, args

    def _arg_parse(self, arg_string, arg_infos):
        '''arg_infos를 기반으로 arg_string을 파싱하여 인자를 리턴한다.'''
        assert(isinstance(arg_string, str))
        assert(isinstance(arg_infos, list))

        args = []

        for arg_info in arg_infos:
            if arg_info == 'msg':
                args.append(arg_string.lstrip())
                break
            
            arg_str, arg_string = self._pop_word(arg_string)
            
            if arg_info == 'int':
                if not arg_str.isdigit():
                    return False, ()
                args.append(int(arg_str))
            else:
                args.append(arg_str)

        return True, tuple(args)
    
    def _pop_word(self, input_string):
        '''명령의 첫번째 단어와 이를 제외한 문장을 리턴한다.'''
        lstrip_string = input_string.lstrip()
        left_index = lstrip_string.find(' ')

        if left_index != -1:
            word = lstrip_string[:left_index]
            result_string = lstrip_string[left_index:]
        else:
            word = lstrip_string
            result_string = ''

        return word, result_string
