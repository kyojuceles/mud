from ..gamelogic.components import factory
from ..gamelogic.world.world import World
from ..gamelogic.world.map   import Map
from ..gamelogic.processor import GameLogicProcessor
from ..gamelogic.processor import GameLogicProcessorEvent
from ..gamelogic.processor import Parser
from ..gamelogic.components.entity import GocEntity

def test_has_components_with_create_hero():
    hero = factory.create_object('hero', -1, 100, 10, 1, 1)
    assert hero.has_component('GocAttribute')
    assert hero.has_component('GocBehaviour')
    assert hero.has_component('GocUpdater')
    assert hero.get_name() == 'hero'

    attribute = hero.get_component('GocAttribute')
    assert attribute.hp == 100
    assert attribute.atk == 10
    assert attribute.armor == 1
    assert attribute.spd == 1

def test_player_after_add_player_to_world():
    player = factory.create_object('player', -1, 100, 10, 1, 1)
    world = World()
    world.add_player(player)

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


def test_move_with_player():
    processor = GameLogicProcessor(TestGameLogicProcessorEvent())
    processor.start()
    world = processor.get_world()

    map1 = Map(GameLogicProcessor.ENTER_ROOM_ID)
    map2 = Map('광장_00_01')
    map3 = Map('광장_00_02')

    map1.add_visitable_map('남', map2)
    map1.add_visitable_map('북', map3)

    map2.add_visitable_map('북', map1)
    map3.add_visitable_map('남', map1)

    world.add_map(map1)
    world.add_map(map2)
    world.add_map(map3)

    processor.dispatch_message(GameLogicProcessor.CONSOLE_PLAYER_ID, '접속')
    player = processor.get_player(GameLogicProcessor.CONSOLE_PLAYER_ID)
    entity = player.get_component('GocEntity')
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == GameLogicProcessor.ENTER_ROOM_ID
    assert player == current_map.get_object(player.get_name())

    prev_map = current_map
    processor.dispatch_message(GameLogicProcessor.CONSOLE_PLAYER_ID, '남')
    current_map = entity.get_map()
    assert prev_map.get_object(player.get_name()) == None
    assert current_map is not None
    assert current_map.get_id() == '광장_00_01'
    assert player == current_map.get_object(player.get_name())
    
    processor.dispatch_message(GameLogicProcessor.CONSOLE_PLAYER_ID, '하늘')
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_01'

    processor.dispatch_message(GameLogicProcessor.CONSOLE_PLAYER_ID, '북')
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_00'

    processor.dispatch_message(GameLogicProcessor.CONSOLE_PLAYER_ID, '북')
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_02'

    processor.dispatch_message(GameLogicProcessor.CONSOLE_PLAYER_ID, '남')
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
    player = factory.create_object('플레이어', -1, 100, 10, 1, 1)
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
    player1 = factory.create_object('플레이어', 0, 100, 10, 1, 1)
    player2 = factory.create_object('플레이어', 1, 100, 10, 1, 1)
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
    player = factory.create_object('플레이어', 0, 100, 10, 1, 1)
    map = Map('테스트맵', '테스트맵', '정적이 흐르는 방')
    map2 = Map('테스트맵2', '테스트맵2', '정적이 흐르는 방')
    map.add_visitable_map('남', map2)
    map.enter_map(player)
    
    map_desc = map.get_desc()
    assert map_desc == '테스트맵\n정적이 흐르는 방\n[남]\n[플레이어]이 서 있습니다.\n'

def test_start_battle_with_behaviour():
    attacker = factory.create_object('공격자', 0, 100, 10, 1, 1)
    target = factory.create_object('방어자', 1, 100, 10, 1, 1)
    map = Map('테스트맵', '테스트맵', '정적이 흐르는 방')
    attacker.get_component('GocEntity').set_map(map)
    map.enter_map(attacker)
    map.enter_map(target)
    
    behaviour = attacker.get_component('GocBehaviour')
    behaviour.start_battle('방어자')

    assert attacker.get_component('GocEntity').get_status() == GocEntity.STATUS_BATTLE
    assert target.get_component('GocEntity').get_status() == GocEntity.STATUS_BATTLE

    for _ in range(0, 10):
        attacker.get_component('GocUpdater').update()
        target.get_component('GocUpdater').update()
    
    assert attacker.get_component('GocAttribute').hp == 10
    assert target.get_component('GocAttribute').hp == 10






