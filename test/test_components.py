from gamelogic.components import factory
from gamelogic.world.world import World
from gamelogic.world.map   import Map
from gamelogic.processor import GameLogicProcessor
from gamelogic.processor import GameLogicProcessorEvent
from gamelogic.command_dispatcher import CommandDispatcher

def test_has_components_with_create_hero():
    hero = factory.create_object('hero', 100, 10, 1, 1)
    assert hero.has_component('GocAttribute')
    assert hero.has_component('GocBehaviour')
    assert hero.has_component('GocUpdater')
    assert hero.name == 'hero'

    attribute = hero.get_component('GocAttribute')
    assert attribute.hp == 100
    assert attribute.atk == 10
    assert attribute.armor == 1
    assert attribute.spd == 1

def test_target_hp_after_attack():
    actor = factory.create_object('actor', 100, 10, 1, 1)
    target = factory.create_object('target', 100, 10, 1, 1)
    actor.get_component('GocBehaviour').attack(target)

    attribute = target.get_component('GocAttribute')
    assert attribute.hp == 91
    
    actor.get_component('GocBehaviour')
    
def test_die_after_attack():
    actor = factory.create_object('actor', 100, 10, 1, 1)
    target = factory.create_object('target', 100, 10, 1, 1)
    behaviour = actor.get_component('GocBehaviour')
    for _ in range(1, 15):
        behaviour.attack(target)
    
    attribute = target.get_component('GocAttribute')
    assert attribute.hp == 0
    assert attribute.is_die()

def test_player_after_add_player_to_world():
    player = factory.create_object('player', 100, 10, 1, 1)
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
        pass


def test_move_with_player():
    processor = GameLogicProcessor(TestGameLogicProcessorEvent())
    processor.start()
    world = GameLogicProcessor.get_world()

    map1 = Map('광장_00_00')
    map2 = Map('광장_00_01')
    map3 = Map('광장_00_02')

    map1.add_visitable_map('남', map2)
    map1.add_visitable_map('북', map3)

    map2.add_visitable_map('북', map1)
    map3.add_visitable_map('남', map1)

    world.add_map(map1)
    world.add_map(map2)
    world.add_map(map3)

    player = factory.create_object('플레이어', 100, 10, 1, 1)
    world.add_player(player)

    behaviour = player.get_component('GocBehaviour')
    entity = player.get_component('GocEntity')

    behaviour.enter_map('광장_00_00')
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_00'

    behaviour.visit_map('남')
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_01'

    behaviour.visit_map('하늘')
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_01'

    behaviour.visit_map('북')
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_00'

    behaviour.visit_map('북')
    current_map = entity.get_map()
    assert current_map is not None
    assert current_map.get_id() == '광장_00_02'

    behaviour.visit_map('남')
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

def test_command_dispatcher():
    processor = GameLogicProcessor(TestGameLogicProcessorEvent())
    dispatcher = CommandDispatcher(processor)
    processor.start()
    world = GameLogicProcessor.get_world()

    map1 = Map('광장_00_00')
    map2 = Map('광장_00_01')
    map3 = Map('광장_00_02')

    map1.add_visitable_map('남', map2)
    map1.add_visitable_map('북', map3)

    map2.add_visitable_map('북', map1)
    map3.add_visitable_map('남', map1)

    world.add_map(map1)
    world.add_map(map2)
    world.add_map(map3)

    dispatcher.dispatch(0, '접속')
    player = dispatcher.get_player(0)
    behaviour = player.get_component('GocBehaviour')
    behaviour.enter_map('광장_00_00')
    entity = player.get_component('GocEntity')
    assert entity.get_map() is not None
    assert entity.get_map().get_id() == '광장_00_00'

    dispatcher.dispatch(0, '남')
    assert entity.get_map() is not None
    assert entity.get_map().get_id() == '광장_00_01'

    processor.stop()