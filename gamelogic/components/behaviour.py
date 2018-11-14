from .gameobject import GameObject
from .gameobject import Component
from .entity import GocEntity
from .attribute import GocAttribute
from ..world.map import Map
from ..world.world import World
from ..global_instance import GlobalInstance
from .network import GocNetworkBase

class GocBehaviour(Component):

    def start_battle(self, target_name: str) -> bool:
        actor_entity: GocEntity = self.get_component(GocEntity)
        current_map = actor_entity.get_map()
        if current_map is None:
            return False

        target = current_map.get_object(target_name)
        if target is None:
            self.get_component(GocNetworkBase).send('대상이 존재하지 않습니다.\n')
            return False

        target_entity: GocEntity = target.get_component(GocEntity)

        if actor_entity.get_status() != GocEntity.STATUS_IDLE or \
           target_entity.get_status() == GocEntity.STATUS_DEATH:
            self.get_component(GocNetworkBase).send('대상을 공격할 수 없습니다.\n')
            return False

        actor_entity.set_status(GocEntity.STATUS_BATTLE)
        actor_entity.set_target(target)
        
        return True


    def attack(self, target: GameObject):
        if not target.has_component(GocBehaviour):
            return

        actor_attribute: GocAttribute = self.get_component(GocAttribute)
        target_attribute: GocAttribute = target.get_component(GocAttribute)
        dmg = actor_attribute.atk - target_attribute.armor
        dmg = max(dmg, 0)
        target_attribute.hp = max(target_attribute.hp - dmg, 0)

        self.get_component(GocNetworkBase).send(\
        '당신은 %s에게 %d 데미지를 주었다.(남은체력 %d)\n' % \
        (target.get_name(), dmg, target_attribute.hp))

        target.get_component(GocNetworkBase).send(\
        '%s는 당신에게 %d 데미지를 주었다.(남은체력 %d)\n' % \
        (self.get_owner_name(), dmg, target_attribute.hp))

        # 대상이 IDLE 상태에서 공격을 당하면 반격을 한다.
        target_entity: GocEntity = target.get_component(GocEntity)
        if target_entity.get_status() != GocEntity.STATUS_BATTLE:
            target_entity.set_status(GocEntity.STATUS_BATTLE)
            target_entity.set_target(self.get_owner())


    def enter_map(self, map_id: str) -> bool:
        if not self.has_component(GocEntity):
            return False

        world = GlobalInstance.get_world()
        map = world.get_map(map_id)
        if map is None:
            return False

        if not map.enter_map(self.get_owner()):
            return False

        entity: GocEntity = self.get_component(GocEntity)
        entity.set_map(map)
        self.get_component(GocNetworkBase).send(map.get_name() + '으로 들어갑니다.\n')
        self.output_current_map_desc()
        return True

    def move_map(self, dest: str) -> bool:
        if not self.has_component(GocEntity):
            return False

        entity: GocEntity = self.get_component(GocEntity)
        current_map = entity.get_map()
        if current_map is None:
            return False

        dest_map = current_map.get_visitable_map(dest)
        if dest_map is None:
            self.get_component(GocNetworkBase).send('갈 수 없습니다.\n')
            return False

        current_map.leave_map(self.get_owner())
        dest_map.enter_map(self.get_owner())

        entity.set_map(dest_map)
        self.get_component(GocNetworkBase).send(dest + '쪽으로 갑니다.\n')
        self.output_current_map_desc()
        return True

    def output_current_map_desc(self):
        entity: GocEntity = self.get_component(GocEntity)
        current_map = entity.get_map()
        if current_map is None:
            return

        current_map_desc = current_map.get_desc()
        objs = current_map.get_object_list()
        for obj in objs:
            current_map_desc += obj.get_component(GocEntity).get_status_desc()

        self.get_component(GocNetworkBase).send(current_map_desc)

    def output_status(self):
        entity: GocEntity = self.get_component(GocEntity)
        attribute: GocAttribute = self.get_component(GocAttribute)
        status_desc = entity.make_name_title() + '\n'
        status_desc += entity.get_status_desc()
        status_desc += attribute.get_status_desc()

        self.get_component(GocNetworkBase).send(status_desc)
