import gamelogic.global_define as global_define
from typing import List, Tuple, Optional
from .global_instance import GlobalInstance
from .global_instance import GlobalInstanceContainer
from .global_instance import GameLogicProcessorEvent
from .client_info import ClientInfo
from .components.gameobject import GameObject
from .utils.timer import Timer
from .world.world import World
from .world.map import Map
from .components.behaviour import GocBehaviour
from .components import factory
from .components.network import NetworkConsoleEventBase
from .tables.character_table import CharacterTable
from .tables.level_table import LevelTable

class GameLogicProcessor(GlobalInstanceContainer):
    '''
    Game Logic을 처리하는 클래스.
    1. 입력을 받아서 처리하고 결과를 이벤트 클래스에 알려준다.
    2. GameLogicProcessor.get_instance()로 글로벌 instance를 얻을 수 있다.
    ''' 
    def __init__(self,
     event: GameLogicProcessorEvent,
     console_player_event: NetworkConsoleEventBase):
         # member initialize
        assert(isinstance(event, GameLogicProcessorEvent))
        assert(isinstance(console_player_event, NetworkConsoleEventBase))
        self._is_start: bool = False
        self._event: GameLogicProcessorEvent = event
        self._console_player_event: NetworkConsoleEventBase = console_player_event
        self._world: World = World()
        self._update_timer: Timer = Timer(global_define.UPDATE_INTERVAL)
        
        # singleton classes initialize
        GlobalInstance.set_global_instance_container(self)
        CharacterTable.initialize()
        LevelTable.initialize()

        # 테스트용 데이터 테이블 로드
        CharacterTable.instance().init_test()
        LevelTable.instance().init_test()
    
    def __del__(self):
        # singleton classes deinitialize
        LevelTable.deinitialize()
        CharacterTable.deinitialize()
        GlobalInstance.set_global_instance_container(None)

    def init_test(self):
        map1 = Map(global_define.ENTER_ROOM_ID, '광장 입구', '중앙에는 분수대가 있고 많은 사람들이 \
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

        npc1 = factory.create_object_npc(100000)
        self._world.add_npc(npc1)
        npc1.get_component(GocBehaviour).enter_map('광장_00_02')

        npc2 = factory.create_object_npc(100001)
        self._world.add_npc(npc2)
        npc2.get_component(GocBehaviour).enter_map('광장_00_02')

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

    def get_event(self) -> GameLogicProcessorEvent:
        return self._event

    def get_world(self) -> World:
        return self._world
    
    def dispatch_message(self, client_info: ClientInfo, msg: str) -> bool:
        if client_info.get_status() == ClientInfo.STATUS_NOT_CONNECT:
            return False

        if client_info.get_status() == ClientInfo.STATUS_NOT_LOGIN:
            return self._dispatch_message_before_login(client_info, msg)

        return self._dispatch_message_after_login(client_info, msg)

    def _dispatch_message_before_login(self, client_info: ClientInfo, msg: str) -> bool:
        if not msg:
            return False

        player_name = msg
        player: GameObject = None

        #중복접속 체크 
        if (self._world.get_player(player_name) is not None):
            GlobalInstance.get_event().event_output('이미 접속중인 이름입니다. 다시 입력해주세요.\n')
            return False
        
        if client_info.is_console():
            player = factory.create_console_object(\
             player_name, self._console_player_event, 0, 1, 0)
        else:
            player = factory.create_object_player(player_name, 0, 1, 0)
            
        client_info.set_player(player)
        client_info.set_status(ClientInfo.STATUS_LOGIN)
        self._world.add_player(player)
        player.get_component(GocBehaviour).enter_map(global_define.ENTER_ROOM_ID)
        return True

    def _dispatch_message_after_login(self, client_info: ClientInfo, msg: str) -> bool:
        ret, cmd, args = Parser.cmd_parse(msg)

        player = client_info._player
        if (player is None):
            return False

        if not ret:
            self._event.event_output('잘못된 명령입니다.\n')
            return False
        
        behaviour: GocBehaviour = player.get_component(GocBehaviour)

        # 이동 처리
        if cmd in ('동', '서', '남', '북'):
            behaviour.move_map(cmd)
            return True

        # 공격 처리
        if cmd == '공격':
            behaviour.start_battle(args[0])
            return True

        # 맵 보기 처리
        if cmd == '본다':
            behaviour.output_current_map_desc()
            return True

        # 플레이어 상태 보기 처리
        if cmd == '상태':
            behaviour.output_status()
            return True

        # 도망 처리
        if cmd == '도망':
            behaviour.flee()
            return True

        # 재시작 처리
        if cmd == '재시작':
            behaviour.respawn()
            return True

        self._event.event_output('잘못된 명령입니다.\n')
        return False

class Parser:
    arg_infos_list = {'공격': ['str']}

    @staticmethod
    def cmd_parse(msg: str):
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
    def _arg_parse(arg_string: str,
         arg_infos: List[Optional[str]]):
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
    def _pop_word(input_string: str):
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
