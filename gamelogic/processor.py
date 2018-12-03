import gamelogic.global_define as global_define
import gamelogic.utils.encrypt as encrypt
import db.db_processor_mysql as db_processor
from typing import List, Tuple, Optional
from .client_info import ClientInfo
from .global_instance import GlobalInstance
from .global_instance import GlobalInstanceContainer
from .global_instance import GameLogicProcessorEvent
from .components.gameobject import GameObject
from .utils.timer import Timer
from .world.world import World
from .world.map import Map
from .world.map import RespawnInfo
from .components.behaviour import GocBehaviour
from .components.entity import GocEntity
from .components.network import GocNetworkBase
from .components.team_attribute import GocTeamAttribute
from .components.database import GocDatabase
from .components import factory
from .tables.character_table import CharacterTable
from .tables.level_table import LevelTable
from .tables.item_table import ItemTable

class GameLogicProcessor(GlobalInstanceContainer):
    '''
    Game Logic을 처리하는 클래스.
    1. 입력을 받아서 처리하고 결과를 이벤트 클래스에 알려준다.
    2. GameLogicProcessor.get_instance()로 글로벌 instance를 얻을 수 있다.
    ''' 
    def __init__(self, event: GameLogicProcessorEvent):
         # member initialize
        assert(isinstance(event, GameLogicProcessorEvent))
        self._is_start: bool = False
        self._event: GameLogicProcessorEvent = event
        self._world: World = World()
        self._update_timer: Timer = Timer(global_define.UPDATE_INTERVAL)
    
    def initialize(self):
        # singleton classes initialize
        GlobalInstance.set_global_instance_container(self)
        CharacterTable.initialize()
        LevelTable.initialize()
        ItemTable.initialize()

        # 테스트용 데이터 테이블 로드
        CharacterTable.instance().init_test()
        LevelTable.instance().init_test()
        ItemTable.instance().init_test()
    
    def deinitialize(self):
        # singleton classes deinitialize
        ItemTable.deinitialize()
        LevelTable.deinitialize()
        CharacterTable.deinitialize()
        GlobalInstance.set_global_instance_container(None)

    def init_test(self):
        map1 = Map(global_define.ENTER_ROOM_ID, '광장 입구', '중앙에는 분수대가 있고 많은 사람들이 \
분주하게 움직이고 있다.')
        map2 = Map('광장_00_01', '광장 남쪽', '북쪽으로 분수대가 보인다. 많은 사람들이 분주하게 움직이고 있다.')
        
        respawn_info_list = []
        respawn_info_list.append(RespawnInfo(100000, 2))
        respawn_info_list.append(RespawnInfo(100001, 1))
        map3 = Map('광장_00_02', '광장 북쪽', '남쪽으로 분수대가 보인다. 북쪽으로 커다란 성이 보인다.\n\
하지만 경비병들이 막아서고 있어서 들어가진 못할 것 같다.', respawn_info_list)

        map1.add_visitable_map('남', map2)
        map1.add_visitable_map('북', map3)

        map2.add_visitable_map('북', map1)
        map3.add_visitable_map('남', map1)

        self._world.add_map(map1)
        self._world.add_map(map2)
        self._world.add_map(map3)

        self._world.respawn_npcs()

    def start(self):
        self._is_start = True
        GlobalInstance.get_event().event_output('서버를 시작합니다\n')
    
    def stop(self):
        self._is_start = False
        GlobalInstance.get_event().event_output('서버를 종료합니다\n')

    async def update(self):
        #게임을 종료한 플레이어 처리.
        objs = self._world.get_object_list()
        for obj in objs:
            entity: GocEntity = obj.get_component(GocEntity)
            team_attribute: GocTeamAttribute = obj.get_component(GocTeamAttribute)
            if entity.is_destroy():
                #플레이어인 경우 종료시에 필요한 database 업데이트
                is_player = team_attribute.is_player()
                if is_player:
                    await obj.get_component(GocDatabase).update_hp()
                self._world.del_object(obj, is_player)

        if not self._is_start:
            return

        if self._update_timer.is_signal():
            await self._world.update()

    def get_event(self) -> GameLogicProcessorEvent:
        return self._event

    def get_world(self) -> World:
        return self._world
    
    def output_welcome_message(self, client_info: ClientInfo):
        client_info.send(global_define.welcome_msg)

    def output_login_name_message(self, client_info: ClientInfo):
        client_info.send(global_define.login_name_msg)
        client_info.set_status(ClientInfo.STATUS_LOGIN_NAME)

    def output_login_password_message(self, client_info: ClientInfo):
        client_info.send(global_define.login_password_msg)
        client_info.set_status(ClientInfo.STATUS_LOGIN_PASSWORD)
        client_info.set_echo_mode(False)

    def output_create_account_name_message(self, client_info: ClientInfo):
        client_info.send(global_define.create_account_name_msg)
        client_info.set_status(ClientInfo.STATUS_CREATE_ACCOUNT_NAME)

    def output_create_account_password_message(self, client_info: ClientInfo):
        client_info.send(global_define.create_account_password_msg)
        client_info.set_status(ClientInfo.STATUS_CREATE_ACCOUNT_PASSWORD)
        client_info.set_echo_mode(False)

    async def dispatch_message(self, client_info: ClientInfo, msg: str):
        if client_info.get_status() == ClientInfo.STATUS_NOT_CONNECT:
            return

        client_status = client_info.get_status()

        #로그인 하기 전의 처리.
        if client_status == ClientInfo.STATUS_LOGIN_NAME:
            await self._dispatch_message_login_name(client_info, msg)
            return
        elif client_status == ClientInfo.STATUS_LOGIN_PASSWORD:
            await self._dispatch_message_login_password(client_info, msg)
            return
        elif client_status == ClientInfo.STATUS_CREATE_ACCOUNT_NAME:
            await self._dispatch_message_create_account_name(client_info, msg)
            return
        elif client_status == ClientInfo.STATUS_CREATE_ACCOUNT_PASSWORD:
            await self._dispatch_message_create_account_password(client_info, msg)
            return

        #로그인이 완료된 이후의 처리.
        await self._dispatch_message_after_login(client_info, msg)
        player: GameObject = client_info.get_player()
        behaviour: GocBehaviour = player.get_component(GocBehaviour)
        behaviour.output_command_prompt()

    async def _dispatch_message_login_name(self, client_info: ClientInfo, msg: str):
        '''로그인:계정 입력 단계를 처리'''
        if not msg:
            return

        if msg in ['새로만들기', 'register']:
            self.output_create_account_name_message(client_info)
            return

        #중복접속 체크
        if self._check_duplicate_login(client_info.get_player_name()):
            client_info.send(global_define.login_name_duplicate_msg)
            self.output_login_name_message(client_info)
            client_info.set_echo_mode(True)
            return

        #존재하는 계정인지 체크한다.
        result = await db_processor.get_player_info(msg)
        if not result:
            client_info.send(global_define.login_name_not_exist_msg)
            return

        client_info.set_player_name(msg)
        self.output_login_password_message(client_info)
    
    async def _dispatch_message_login_password(self, client_info: ClientInfo, msg: str):
        '''로그인:패스워드 입력 단계를 처리'''
        player_name = client_info.get_player_name()
        result = await db_processor.get_player_info(player_name)
        if not result:
            client_info.send(global_define.login_fail_msg)
            self.output_login_name_message(client_info)
            client_info.set_echo_mode(True)
            return

        db_password = result[2]
        player_uid = result[0]
        lv = result[3]
        xp = result[4]
        hp = result[5]

        #패스워드 체크
        if encrypt.encrypt_sha256(msg) != db_password:
            client_info.send(global_define.login_password_invalid_msg)
            return

        #중복접속 체크
        if self._check_duplicate_login(client_info.get_player_name()):
            client_info.send(global_define.login_name_duplicate_msg)
            self.output_login_name_message(client_info)
            client_info.set_echo_mode(True)
            return

        #로그인 처리
        self._login(client_info, player_uid, lv, xp, hp)

        #db에서 아이템리스트를 얻어온다.
        await self._get_item_list_from_database(client_info)
 
    async def _dispatch_message_create_account_name(self, client_info: ClientInfo, msg: str):
        '''계정생성:계정 입력 단계를 처리'''
        if not msg:
            return

        if msg in global_define.ban_account_list:
            client_info.send(global_define.create_account_name_ban_msg)
            return
        
        #존재하는 계정인지 체크한다.
        result = await db_processor.get_player_info(msg)
        if result:
            client_info.send(global_define.create_account_name_already)
            return

        client_info.set_player_name(msg)
        self.output_create_account_password_message(client_info)
    
    async def _dispatch_message_create_account_password(self, client_info: ClientInfo, msg: str):
        '''계정생성:패스워드 입력 단계를 처리'''
        if not msg:
            return

        player_name = client_info.get_player_name()
        if self._check_duplicate_login(player_name):
            client_info.send(global_define.login_name_duplicate_msg)
            self.output_login_name_message(client_info)
            client_info.set_echo_mode(True)
            return

        #계정생성
        encrypt_password = encrypt.encrypt_sha256(msg)
        result, uid = await db_processor.create_account(player_name, encrypt_password)
        if not result:
            client_info.send(global_define.create_account_fail_msg)
            self.output_login_name_message(client_info)
            client_info.set_echo_mode(True)
            return

        #로그인
        self._login(client_info, uid, 1, 0, -1)

    def _login(self, client_info: ClientInfo, player_uid: int, lv: int, xp: int, hp):
        client_info.set_echo_mode(True)
        player_name = client_info.get_player_name()
        player: GameObject = None
        self.output_welcome_message(client_info)
    
        player = factory.create_object_player(player_name, client_info, player_uid, lv, xp, hp)        
        client_info.set_player(player)
        client_info.set_status(ClientInfo.STATUS_LOGIN)
        self._world.add_object(player, True)
        player.get_component(GocBehaviour).enter_map(global_define.ENTER_ROOM_ID)
        behaviour: GocBehaviour = player.get_component(GocBehaviour)
        behaviour.output_command_prompt()

    async def _get_item_list_from_database(self, client_info: ClientInfo):
        player = client_info.get_player()
        await player.get_component(GocDatabase).get_item_list()

    def _check_duplicate_login(self, player_name: str) -> bool:
        if (self._world.get_player(player_name) is not None):
            return True

        return False

    async def _dispatch_message_after_login(self, client_info: ClientInfo, msg: str):
        ret, cmd, args = Parser.cmd_parse(msg)

        player: GameObject = client_info.get_player()
        if (player is None):
            return

        if not ret:
            client_info.send('잘못된 명령입니다.\n')
            return
        
        behaviour: GocBehaviour = player.get_component(GocBehaviour)

        # 이동 처리
        if cmd in ('동', '서', '남', '북', 'e', 'w', 's', 'n'):
            behaviour.move_map(cmd)
            return

        # 공격 처리
        if cmd in ('공격', 'attack'):
            behaviour.start_battle(args[0])
            return

        # 맵 보기 처리
        if cmd in ('본다', 'see'):
            behaviour.output_current_map_desc()
            return

        # 플레이어 상태 보기 처리
        if cmd in ('상태', 'status'):
            behaviour.output_status()
            return

        # 도망 처리
        if cmd in ('도망', 'flee'):
            behaviour.flee()
            return

        # 재시작 처리
        if cmd in ('재시작', 'respawn'):
            behaviour.respawn()
            return

        # 말하기 처리
        if cmd in ('말하기', 'say'):
            behaviour.say(args[0])
            return

        # 외치기 처리
        if cmd in ('외치기', 'shout'):
            behaviour.say_to_world(args[0])
            return

        # 소지품 처리
        if cmd in ('소지품', 'inventory'):
            behaviour.output_inventory()
            return

        # 종료 처리
        if cmd in ('나가기', 'exit'):
            network_base: GocNetworkBase = player.get_component(GocNetworkBase)
            network_base.disconnect()
            return
        
        # 도움말 처리
        if cmd in ('도움말', 'help'):
            behaviour.output_help_msg()
            return

        client_info.send('잘못된 명령입니다.\n')

class Parser:
    arg_infos_list =\
     {'공격': ['str'], '말하기': ['msg'], '외치기': ['msg'], 'attack': ['str'], 'say': ['str'], 'shout': ['str']}

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
