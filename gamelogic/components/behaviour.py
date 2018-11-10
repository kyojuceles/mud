from .gameobject import Component
from .entity import GocEntity
from ..global_instance import GlobalInstance

class GocBehaviour(Component):
    name = 'GocBehaviour'

    def start_battle(self, target):
        actor_entity = self.get_component('GocEntity')
        target_entity = target.get_component('GocEntity')

        if actor_entity.get_status() != GocEntity.STATUS_IDLE and \
           target_entity.get_status() == GocEntity.STATUS_DEATH:
            return False

        actor_entity.set_status(GocEntity.STATUS_BATTLE)
        target_entity.set_status(GocEntity.STATUS_BATTLE)
        return True


    def attack(self, target):
        if not target.has_component('GocBehaviour'):
            return

        actorAttribute = self.get_component('GocAttribute')
        targetAttribute = target.get_component('GocAttribute')
        dmg = actorAttribute.atk - targetAttribute.armor
        dmg = max(dmg, 0)
        targetAttribute.hp = max(targetAttribute.hp - dmg, 0)

        print('%s가 %s에게 %d 데미지를 주었다.' % (self.get_owner_name(), target.get_name(), dmg))
        print('%s의 체력은 %d이 되었다.' % (target.get_name(), targetAttribute.hp))

        if targetAttribute.is_die():
            print('%s는 사망했다.' % target.get_name())

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