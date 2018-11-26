import typing
import asyncio
import gamelogic.global_define as global_define
import gamelogic.utils.encrypt as encrypt
from ..gamelogic.global_instance import GlobalInstance
from ..gamelogic.global_instance import GlobalInstanceContainer
from ..gamelogic.components.attribute import GocAttribute
from ..gamelogic.components.behaviour import GocBehaviour
from ..gamelogic.components.updater import GocUpdaterBase
from ..gamelogic.components import factory
from ..gamelogic.world.world import World
from ..gamelogic.world.map import Map
from ..gamelogic.world.map import RespawnInfo
from ..gamelogic.processor import GameLogicProcessor
from ..gamelogic.processor import GameLogicProcessorEvent
from ..gamelogic.processor import Parser
from ..gamelogic.components.entity import GocEntity
from ..gamelogic.tables.level_table import LevelTable
from ..gamelogic.tables.character_table import CharacterTable
from ..gamelogic.components.network import GocNetworkBase
from ..gamelogic.client_info import ClientInfo
from ..gamelogic.tables.character_table import CharacterTable

def test_has_components_with_create_hero():
    hero = factory.create_object_npc_with_attribute('hero', -1, 100, 10, 1, 1, 0)
    assert hero.has_component(GocAttribute)
    assert hero.has_component(GocBehaviour)
    assert hero.has_component(GocUpdaterBase)
    assert hero.get_name() == 'hero'

    attribute: GocAttribute = hero.get_component(GocAttribute)
    assert attribute.hp == 100
    assert attribute.atk == 10
    assert attribute.armor == 1
    assert attribute.spd == 1

def test_player_after_add_player_to_world():
    player = factory.create_object_npc_with_attribute('player', -1, 100, 10, 1, 1, 0)
    world = World()
    world.add_object(player, True)

    assert world.get_player('player') is not None
    assert world.get_player('player2') is None

def test_map_after_add_map_to_world():
    world = World()
    world.add_map(Map('광장_00_01'))

    assert world.get_map('광장_00_01') is not None
    assert world.get_map('광장_00,00') is None

class TestGameLogicProcessorEvent(GameLogicProcessorEvent):
    
    def event_output(self, output):
        print(output, end = '')

class TestNetworkConsoleEvent():
    
    def on_receive(self, msg):
        print(msg, end = '')

def test_move_with_player():
    processor = GameLogicProcessor(
        TestGameLogicProcessorEvent())
    processor.start()
    world = processor.get_world()

    map1 = Map(global_define.ENTER_ROOM_ID)
    map2 = Map('광장_00_01')
    map3 = Map('광장_00_02')

    map1.add_visitable_map('남', map2)
    map1.add_visitable_map('북', map3)

    map2.add_visitable_map('북', map1)
    map3.add_visitable_map('남', map1)

    world.add_map(map1)
    world.add_map(map2)
    world.add_map(map3)

    loop = asyncio.get_event_loop()

    client_info = ClientInfo()
    client_info.set_player_name('플레이어')
    processor._login(client_info, 0, 1, 0, -1)

    player = client_info.get_player()
    entity: GocEntity = player.get_component(GocEntity)
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == global_define.ENTER_ROOM_ID
    assert player == current_map.get_object(player.get_name())

    prev_map = current_map
    loop.run_until_complete(processor.dispatch_message(client_info, '남'))
    current_map = entity.get_map()
    assert prev_map.get_object(player.get_name()) == None
    assert current_map is not None
    assert current_map.get_id() == '광장_00_01'
    assert player == current_map.get_object(player.get_name())
    
    loop.run_until_complete(processor.dispatch_message(client_info, '하늘'))
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_01'

    loop.run_until_complete(processor.dispatch_message(client_info, '북'))
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_00'

    loop.run_until_complete(processor.dispatch_message(client_info, '북'))
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_02'

    loop.run_until_complete(processor.dispatch_message(client_info, '남'))
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_00'

    processor.stop()

def test_dest_after_add_dest_to_map():
    map1 = Map('광장_00_00')
    map2 = Map('광장_00_01')
    map3 = Map('광장_00_02')

    map1.add_visitable_map('남', map2)
    map1.add_visitable_map('북', map3)

    assert map1.get_visitable_map('남') is map2
    assert map1.get_visitable_map('동') is None
    assert map1.get_visitable_map('북') is map3

    result = map1.get_visitable_map_list()
    assert ('남', '광장_00_01') in result
    assert ('북', '광장_00_02') in result
    assert len(result) == 2

def test_command_parse():
    # 입력받은 커맨드의 파싱을 테스트

    atk_cmd = " 공격 경비병"
    move_cmd = " 북"
    test_arg_string = "100 200"
    test2_arg_string = "100 병사"

    ret, cmd, args = Parser.cmd_parse(atk_cmd)
    assert ret == True and cmd == '공격' and args == ('경비병',)

    ret, cmd, args = Parser.cmd_parse(move_cmd)
    assert ret == True and cmd == '북' and args == ()

    ret, args = Parser._arg_parse(test_arg_string, ['int', 'int'])
    assert ret == True and args == (100, 200)
    
    ret, args = Parser._arg_parse(test2_arg_string, ['int', 'str'])
    assert ret == True and args == (100, '병사')

    ret, args = Parser._arg_parse(test2_arg_string, ['msg'])
    assert ret == True and args == (test2_arg_string,)

def test_game_object_enter_leave_map():
    player = factory.create_object_npc_with_attribute('플레이어', -1, 100, 10, 1, 1, 0)
    map = Map('테스트맵', '테스트맵', '정적이 흐르는 방')
    map.enter_map(player)
    obj = map.get_object('플레이어')
    assert obj.get_name() == '플레이어'
    
    obj_list = map.get_object_list()
    assert len(obj_list) == 1
    assert obj_list[0].get_name() == '플레이어'  

    map.leave_map(player)
    obj = map.get_object('플레이어')
    assert obj == None

def test_order_of_object_in_map():
    player1 = factory.create_object_npc_with_attribute('플레이어', 0, 100, 10, 1, 1, 0)
    player2 = factory.create_object_npc_with_attribute('플레이어', 1, 100, 10, 1, 1, 0)
    map = Map('테스트맵', '테스트맵', '정적이 흐르는 방')
    map.enter_map(player1)
    map.enter_map(player2)
    obj = map.get_object('1.플레이어')
    assert obj.get_id() == 0

    obj = map.get_object('2.플레이어')
    assert obj.get_id() == 1

    obj_list = map.get_object_list()
    assert len(obj_list) == 2
    assert obj_list[0].get_id() == 0
    assert obj_list[1].get_id() == 1

def test_output_map_desc():
    player = factory.create_object_npc_with_attribute('플레이어', 0, 100, 10, 1, 1, 0)
    map = Map('테스트맵', '테스트맵', '정적이 흐르는 방')
    map2 = Map('테스트맵2', '테스트맵2', '정적이 흐르는 방')
    map.add_visitable_map('남', map2)
    map.enter_map(player)
    
    map_desc = map.get_desc()
    assert map_desc == '[테스트맵]\n정적이 흐르는 방\n[남]\n'

def test_start_battle_with_behaviour():
    attacker = factory.create_object_npc_with_attribute('공격자', 0, 100, 10, 1, 1, 0)
    target = factory.create_object_npc_with_attribute('방어자', 1, 100, 10, 1, 1, 1)
    map = Map('테스트맵', '테스트맵', '정적이 흐르는 방')
    attacker.get_component(GocEntity).set_map(map)
    map.enter_map(attacker)
    map.enter_map(target)

    attacker.get_component(GocEntity).set_map(map)
    target.get_component(GocEntity).set_map(map)
    
    behaviour = attacker.get_component(GocBehaviour)
    behaviour.start_battle('방어자')

    assert attacker.get_component(GocEntity).get_status() == GocEntity.STATUS_BATTLE
    assert target.get_component(GocEntity).get_status() == GocEntity.STATUS_IDLE

    loop = asyncio.get_event_loop()
    for _ in range(0, 10):
        loop.run_until_complete(attacker.get_component(GocUpdaterBase).update())
        loop.run_until_complete(target.get_component(GocUpdaterBase).update())

    assert attacker.get_component(GocEntity).get_status() == GocEntity.STATUS_BATTLE
    assert target.get_component(GocEntity).get_status() == GocEntity.STATUS_BATTLE        
    
    assert attacker.get_component(GocAttribute).hp == 10
    assert target.get_component(GocAttribute).hp == 10

def test_data_tables():
    table = LevelTable.initialize()
    table.add_row(1, 100, 100, 10, 1, 1)
    table.add_row(2, 200, 150, 12, 1, 1)
    table.add_row(3, 300, 200, 14, 2, 1)
    table.add_row(4, 400, 250, 16, 2, 1)
    table.add_row(5, 500, 300, 18, 1, 1)

    level_info_1 = LevelTable.get_lv_info(1)
    level_info_3 = LevelTable.get_lv_info(3)
    level_info_6 = LevelTable.get_lv_info(6)

    assert level_info_1.max_hp == 100
    assert level_info_1.atk == 10
    assert level_info_1.armor == 1
    assert level_info_1.spd == 1

    assert level_info_3.max_hp == 200
    assert level_info_3.atk == 14
    assert level_info_3.armor == 2
    assert level_info_3.spd == 1

    assert level_info_6 is None

    chr_table = CharacterTable.initialize()
    chr_table.add_row(1000, '경비병', 10, 100, 10, 1, 1)
    chr_table.add_row(1001, '경비대장', 100, 150, 12, 1, 1)

    chr_info_1000 = CharacterTable.get_chr_info(1000)
    chr_info_1001 = CharacterTable.get_chr_info(1001)
    chr_info_1002 = CharacterTable.get_chr_info(1002)

    assert chr_info_1000.name == '경비병'
    assert chr_info_1000.gain_xp == 10
    assert chr_info_1000.max_hp == 100
    assert chr_info_1000.atk == 10
    assert chr_info_1000.armor == 1
    assert chr_info_1000.spd == 1

    assert chr_info_1001.name
    assert chr_info_1001.gain_xp == 100
    assert chr_info_1001.max_hp == 150
    assert chr_info_1001.atk == 12
    assert chr_info_1001.armor == 1
    assert chr_info_1001.spd == 1

    assert chr_info_1002 is None

def test_just_call_method():
    obj = factory.create_object_npc_with_attribute('플레이어', 0, 100, 10, 0, 0, 0)
    obj.get_component(GocNetworkBase).broadcast_in_map('테스트')
    #obj.get_component(GocNetworkBase).broadcast_in_world('테스트')

def test_recovery_by_percent_hp():
    obj = factory.create_object_npc_with_attribute('플레이어', 0, 100, 10, 0, 0, 0)
    attribute: GocAttribute = obj.get_component(GocAttribute)
    attribute.set_hp(1)
    behaviour: GocBehaviour = obj.get_component(GocBehaviour)
    behaviour.recovery_by_percent(10)
    
    assert attribute.hp == 11

def test_sha256_encryption():
    hash_value = encrypt.encrypt_sha256('abcdefg')
    assert encrypt.encrypt_sha256('abcdefg') == hash_value
    assert encrypt.encrypt_sha256('') != hash_value

class GlobalInstanceContainerTest(GlobalInstanceContainer):
    def __init__(self, world):
        self._world = world
        GlobalInstance.set_global_instance_container(self)

    def get_event(self):
        return self.output_event

    def get_world(self):
        return self._world

    def output_event(self, msg):
        pass

def test_respawn_npcs():
    GlobalInstance.set_global_instance_container(None)
    global_instance: GlobalInstanceContainerTest = GlobalInstanceContainerTest(World())
    CharacterTable.initialize()
    CharacterTable.instance().init_test()

    respawn_info_list = []
    respawn_info_list.append(RespawnInfo(100000, 2))
    respawn_info_list.append(RespawnInfo(100001, 1))
    map = Map('테스트', '테스트', '', respawn_info_list)
    world = GlobalInstance.get_world()
    world.add_map(map)
    world.respawn_npcs()

    objs = map.get_alive_object_list()
    assert objs[0].get_id() == 100000
    assert objs[1].get_id() == 100000
    assert objs[2].get_id() == 100001

    objs[1].get_component(GocAttribute).set_hp(0)
    world.respawn_npcs()
    
    objs = map.get_alive_object_list()
    assert objs[0].get_id() == 100000
    assert objs[1].get_id() == 100000
    assert objs[2].get_id() == 100001

    CharacterTable.deinitialize()













