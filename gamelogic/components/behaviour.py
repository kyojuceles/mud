from .gameobject import Component
from .entity import GocEntity
from ..world.map import Map
from ..global_instance import GlobalInstance

class GocBehaviour(Component):
    name = 'GocBehaviour'

    def start_battle(self, target_name):
        actor_entity = self.get_component('GocEntity')
        current_map = actor_entity.get_map()
        if current_map is None:
            return False

        target = current_map.get_object(target_name)
        if target is None:
            GlobalInstance.get_event().event_output('대상이 존재하지 않습니다.\n')
            return False

        target_entity = target.get_component('GocEntity')

        if actor_entity.get_status() != GocEntity.STATUS_IDLE or \
           target_entity.get_status() == GocEntity.STATUS_DEATH:
            return False

        actor_entity.set_status(GocEntity.STATUS_BATTLE)
        actor_entity.set_target(target)

        if target_entity.get_status() != GocEntity.STATUS_BATTLE:
            target_entity.set_status(GocEntity.STATUS_BATTLE)
            target_entity.set_target(self.get_owner())
        
        return True


    def attack(self, target):
        if not target.has_component('GocBehaviour'):
            return

        actor_attribute = self.get_component('GocAttribute')
        target_attribute = target.get_component('GocAttribute')
        dmg = actor_attribute.atk - target_attribute.armor
        dmg = max(dmg, 0)
        target_attribute.hp = max(target_attribute.hp - dmg, 0)

        GlobalInstance.get_event().event_output(\
        '%s가 %s에게 %d 데미지를 주었다.(남은체력 %d)\n' % \
        (self.get_owner_name(), target.get_name(), dmg, target_attribute.hp))


    def enter_map(self, map_id):
        if not self.has_component('GocEntity'):
            return False

        world = GlobalInstance.get_world()
        map = world.get_map(map_id)
        if map is None:
            return False

        if not map.enter_map(self.get_owner()):
            return False

        entity = self.get_component('GocEntity')
        entity.set_map(map)
        GlobalInstance.get_event().event_output(map.get_name() + '으로 들어갑니다.\n')
        self._output_current_map_desc()
        return True

    def move_map(self, dest):
        if not self.has_component('GocEntity'):
            return False

        entity = self.get_component('GocEntity')
        current_map = entity.get_map()
        if current_map is None:
            return False

        dest_map = current_map.get_visitable_map(dest)
        if dest_map is None:
            GlobalInstance.get_event().event_output('갈 수 없습니다.\n')
            return False

        current_map.leave_map(self.get_owner())
        dest_map.enter_map(self.get_owner())

        entity.set_map(dest_map)
        GlobalInstance.get_event().event_output(dest + '쪽으로 갑니다.\n')
        self._output_current_map_desc()
        return True

    def _output_current_map_desc(self):
        entity = self.get_component('GocEntity')
        current_map = entity.get_map()
        if current_map is None:
            return ''

        current_map_desc = current_map.get_desc()
        GlobalInstance.get_event().event_output(current_map_desc)