from .global_instance import GlobalInstance
from .global_instance import GlobalInstanceContainer
from .global_instance import GameLogicProcessorEvent
from .utils import instance_checker
from .utils.timer import Timer
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
    ENTER_ROOM_ID = '광장_00_00'
    CONSOLE_PLAYER_ID = -1
    UPDATE_INTERVAL = 1
     
    def __init__(self, event):
        assert(isinstance(event, GameLogicProcessorEvent))
        self._is_start = False
        self._event = event
        self._world = World()
        self._players = {}
        self._update_timer = Timer(GameLogicProcessor.UPDATE_INTERVAL)
        GlobalInstance.set_global_instance_container(self)

    def init_test(self):
        map1 = Map(GameLogicProcessor.ENTER_ROOM_ID, '광장 입구', '중앙에는 분수대가 있고 많은 사람들이 \
분주하게 움직이고 있다.')
        map2 = Map('광장_00_01', '광장 남쪽', '북쪽으로 분수대가 보인다. 많은 사람들이 분주하게 움직이고 있다.')
        map3 = Map('광장_00_02', '광장 북쪽', '남쪽으로 분수대가 보인다. 북쪽으로 커다란 성이 보인다.\n\
하지만 경비병들이 막아서고 있어서 들어가진 못할 것 같다.')

        map1.add_visitable_map('남', map2)
        map1.add_visitable_map('북', map3)

        map2.add_visitable_map('북', map1)
        map3.add_visitable_map('남', map1)

        self._world.add_map(map1)
        self._world.add_map(map2)
        self._world.add_map(map3)

        npc1 = factory.create_object('경비병', 10000, 100, 1, 0, 1)
        self._world.add_npc(npc1)
        npc1.get_component('GocBehaviour').enter_map('광장_00_02')

        npc2 = factory.create_object('경비병', 10001, 100, 1, 0, 1)
        self._world.add_npc(npc2)
        npc2.get_component('GocBehaviour').enter_map('광장_00_02')

    def start(self):
        self._is_start = True
        GlobalInstance.get_event().event_output('서버를 시작합니다\n')
    
    def stop(self):
        self._is_start = False
        GlobalInstance.get_event().event_output('서버를 종료합니다\n')

    def update(self):
        if not self._is_start:
            return

        if self._update_timer.is_signal():
            self._world.update()

    def get_player(self, id):
        return self._players.get(id)

    def get_event(self):
        return self._event

    def get_world(self):
        return self._world
    
    def dispatch_message(self, id, msg):
        if not self._is_login(id):
            return self._dispatch_message_before_login(id, msg)
        
        return self._dispatch_message_after_login(id, msg)

    def _dispatch_message_before_login(self, id, msg):
        ret, cmd, args = Parser.cmd_parse(msg)

        if not ret:
            self._event.event_output('잘못된 명령입니다.\n')
            return False

        if cmd == '접속':
            if id in self._players:
                return False

            player = factory.create_object('플레이어', -1, 100, 10, 1, 1)
            self._world.add_player(player)
            self._players[id] = player
            player.get_component('GocBehaviour').enter_map(GameLogicProcessor.ENTER_ROOM_ID)
            return True

        self._event.event_output('잘못된 명령입니다.\n')
        return False

    def _dispatch_message_after_login(self, id, msg):
        ret, cmd, args = Parser.cmd_parse(msg)

        player = self.get_player(id)
        if (player is None):
            return False

        if not ret:
            self._event.event_output('잘못된 명령입니다.\n')
            return False
        
        if cmd in ('동', '서', '남', '북'):
            behaviour = player.get_component('GocBehaviour')
            behaviour.move_map(cmd)
            return True

        if cmd == '공격':
            behaviour = player.get_component('GocBehaviour')
            behaviour.start_battle(args[0])
            return True

        self._event.event_output('잘못된 명령입니다.\n')
        return False

    def _is_login(self, id):
        return id in self._players

class Parser:
    arg_infos_list = {'공격': ['str']}

    @staticmethod
    def cmd_parse(msg):
        """
        입력받은 msg 파싱해서 형식에 맞는 cmd와 args를 리턴한다.
        input_string이 적절하지 않으면 False를 리턴한다.
        """
        assert(isinstance(msg, str))

        cmd, result_string = Parser._pop_word(msg)

        if cmd == '':
            return False, '', ()
 
        arg_infos = []
        if cmd in Parser.arg_infos_list:
            arg_infos = Parser.arg_infos_list[cmd]

        ret, args = Parser._arg_parse(result_string, arg_infos)
        return ret, cmd, args

    @staticmethod
    def _arg_parse(arg_string, arg_infos):
        '''arg_infos를 기반으로 arg_string을 파싱하여 인자를 리턴한다.'''
        assert(isinstance(arg_string, str))
        assert(isinstance(arg_infos, list))

        args = []

        for arg_info in arg_infos:
            if arg_info == 'msg':
                args.append(arg_string.lstrip())
                break
            
            arg_str, arg_string = Parser._pop_word(arg_string)
            
            if arg_info == 'int':
                if not arg_str.isdigit():
                    return False, ()
                args.append(int(arg_str))
            else:
                if not arg_str:
                    return False, ()
                args.append(arg_str)

        return True, tuple(args)
    
    @staticmethod
    def _pop_word(input_string):
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
