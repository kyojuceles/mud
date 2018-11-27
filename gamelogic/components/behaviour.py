#behaviour.py
import random
import gamelogic.global_define as global_define
from .gameobject import GameObject
from .gameobject import Component
from .entity import GocEntity
from .attribute import GocAttribute
from .team_attribute import GocTeamAttribute
from .inventory import GocInventory
from ..item.item import Item
from ..world.map import Map
from ..world.world import World
from ..global_instance import GlobalInstance
from .network import GocNetworkBase

class GocBehaviour(Component):
    '''
    캐릭터들의 이동, 공격, 상태, 맵 보기 등의 기능들을 처리하는 컴포넌트.
    캐릭터들의 행동들은 대부분 이 컴포넌트를 통해서 시작됨
    '''
    def __init__(self):
        super().__init__()        

    def start_battle(self, target_name: str) -> bool:
        actor_entity: GocEntity = self.get_component(GocEntity)
        current_map = actor_entity.get_map()
        if current_map is None:
            return False

        #공격하려는 대상이 맵안에 있는지 체크
        target = current_map.get_object(target_name)
        if target is None:
            self.get_component(GocNetworkBase).send('대상이 존재하지 않습니다.\n')
            return False

        #공격할 수 있는 상태인지 체크
        if actor_entity.is_die():
            self.get_component(GocNetworkBase).send('사망한 상태에서는 공격을 할 수 없습니다.\n')
            return False

        if actor_entity.is_battle():
            self.get_component(GocNetworkBase).send('전투중에는 다른 대상을 공격할 수 없습니다.\n')
            return False
        ######################
        
        #대상이 적군인지 체크(아군이면 공격할 수 없다)
        team_attribute: GocTeamAttribute = self.get_component(GocTeamAttribute)
        if team_attribute.is_ally(target):
            self.get_component(GocNetworkBase).send('아군은 공격할 수 없습니다.\n')
            return False

        #대상이 살아 있는지 체크
        target_entity: GocEntity = target.get_component(GocEntity)
        if target_entity.get_status() == GocEntity.STATUS_DEATH:
            self.get_component(GocNetworkBase).send('사망한 대상은 공격할 수 없습니다.\n')
            return False

        actor_entity.set_status(GocEntity.STATUS_BATTLE)
        actor_entity.set_target(target)
        
        return True
    
    def respawn(self) -> bool:
        '''
        죽었을때 리스폰 방에서 부활하는 함수(재시작)
        '''
        team_attribute: GocTeamAttribute = self.get_component(GocTeamAttribute)
        if not team_attribute.is_player():
            return False

        entity: GocEntity = self.get_component(GocEntity)
        if not entity.is_die():
            self.get_component(GocNetworkBase).send('재시작은 사망한 상태에만 할 수 있습니다.\n')
            return False

        behaviour: GocBehaviour = self.get_component(GocBehaviour)
        behaviour.leave_map()
        behaviour.enter_map(global_define.ENTER_ROOM_ID)

        attribute: GocAttribute = self.get_component(GocAttribute)
        attribute.set_hp(1)
        entity.set_status(GocEntity.STATUS_IDLE)

    def recovery_by_percent(self, percent: int) -> bool:
        '''
        최대 hp의 퍼센트만큼을 회복한다.
        percent의 범위는 1~100
        '''
        if percent < 1: return False
        if percent > 100 : percent = 100

        attribute: GocAttribute = self.get_component(GocAttribute)
        max_hp = attribute.max_hp
        amount = int(max_hp * (percent / 100))
        attribute.set_hp(attribute.hp + amount)

        return True

    def say(self, msg):
        '''방에 있는 구성원들에게 말하는 기능'''
        network_base: GocNetworkBase = self.get_component(GocNetworkBase)
        network_base.broadcast_in_map('%s님이 "%s"라고 말했습니다.\n' % (self.get_owner_name_title(), msg), True)
        network_base.send('당신이 "%s"라고 말했습니다.\n' % msg)

    def say_to_world(self, msg):
        '''월드에 있는 모든 플레이어들에게 말하는 기능'''
        network_base: GocNetworkBase = self.get_component(GocNetworkBase)
        network_base.broadcast_in_world('%s님이 "%s"라고 외쳤습니다.\n' % (self.get_owner_name_title(), msg), True)
        network_base.send('당신이 "%s"라고 외쳤습니다.\n' % msg)       

    def output_inventory(self):
        '''소지품 리스트를 보여주는 기능'''
        network_base:GocNetworkBase = self.get_component(GocNetworkBase)
        inventory: GocInventory = self.get_component(GocInventory)
        item_list = inventory.get_item_list()
        network_base.send('[소지품]\n')
        for item in item_list: #type: Item
            network_base.send(item.get_name() + '\n')

    def flee(self) -> bool:
        entity: GocEntity = self.get_component(GocEntity)
        
        #도망 가능한 상태인지 체크
        if not entity.is_battle():
            self.get_component(GocNetworkBase).send('전투중이 아닐때는 도망갈 수 없습니다.\n')
            return False

        #이번 턴에 도망을 시도 한적이 있으면 다음 턴까지는 도망을 시도할 수 없다.
        if entity.is_try_flee():
            return False

        #맵에 도망칠수 있는 곳이 있는지 체크
        current_map = entity.get_map()
        can_flee_map_list = current_map.get_visitable_map_dest_list()
        if not can_flee_map_list:
            self.get_component(GocNetworkBase).send('도망갈 수 있는 곳이 없습니다.\n')
            return False

        entity.try_flee()

        #50프로의 확률로 도망(임시)
        random_number = random.random()
        if random_number < 0.5:
            self.get_component(GocNetworkBase).send('도망치려 했으나 실패했습니다.\n')
            return False

        #어느 맵으로 도망갈지 정함
        flee_map_index = random.randrange(len(can_flee_map_list))
        flee_map_dest = can_flee_map_list[flee_map_index]
        entity.set_status(GocEntity.STATUS_IDLE)
        if not self.move_map(flee_map_dest):
            self.get_component(GocNetworkBase).send('도망치려 했으나 실패했습니다.\n')
            return False

        self.get_component(GocNetworkBase).broadcast_in_map(\
         '%s가 [%s]쪽으로 도망쳤습니다.\n' % (self.get_owner_name_title(), flee_map_dest),
         True)
        self.get_component(GocNetworkBase).send('당신은 도망쳤습니다. 전투를 종료합니다.\n')
        return True
    
    def attack(self, target: GameObject):
        if not target.has_component(GocBehaviour):
            return

        actor_attribute: GocAttribute = self.get_component(GocAttribute)
        target_attribute: GocAttribute = target.get_component(GocAttribute)
        dmg = actor_attribute.atk - target_attribute.armor
        dmg = max(dmg, 0)
        target_attribute.set_hp(target_attribute.hp - dmg)

        self.get_component(GocNetworkBase).send(\
        '당신은 %s에게 %d 데미지를 입혔습니다.(남은체력 %d)\n' % \
        (target.get_name(), dmg, target_attribute.hp))

        target.get_component(GocNetworkBase).send(\
        '%s는 당신에게 %d 데미지를 입혔습니다.(남은체력 %d)\n' % \
        (self.get_owner_name(), dmg, target_attribute.hp))

        # 대상이 IDLE 상태에서 공격을 당하면 반격을 한다.
        target_entity: GocEntity = target.get_component(GocEntity)
        if target_entity.get_status() != GocEntity.STATUS_BATTLE:
            target_entity.set_status(GocEntity.STATUS_BATTLE)
            target_entity.set_target(self.get_owner())


    def enter_map(self, map_id: str) -> bool:
        if not self.has_component(GocEntity):
            return False

        world: World = GlobalInstance.get_world()
        map = world.get_map(map_id)
        if map is None:
            return False

        if not map.enter_map(self.get_owner()):
            return False

        entity: GocEntity = self.get_component(GocEntity)
        entity.set_map(map)
        self.get_component(GocNetworkBase).broadcast_in_map(
            '%s가 들어왔습니다.\n' % self.get_owner_name_title(), True)
        self.get_component(GocNetworkBase).send(map.get_name() + '으로 들어갑니다.\n')
        self.output_current_map_desc()
        return True

    def leave_map(self) -> bool:
        entity: GocEntity = self.get_component(GocEntity)
        map = entity.get_map()
        if map is None:
            return False

        self.get_component(GocNetworkBase).broadcast_in_map(
            '%s가 나갔습니다.\n' % self.get_owner_name_title(), True)
        entity.set_map(None)
        return map.leave_map(self.get_owner())

    def move_map(self, dest: str) -> bool:
        if not self.has_component(GocEntity):
            return False

        entity: GocEntity = self.get_component(GocEntity)
        #이동 가능한 상태인지 체크
        if entity.is_battle():
            self.get_component(GocNetworkBase).send('전투중에는 이동할 수 없습니다.\n')
            return False

        if entity.is_die():
            self.get_component(GocNetworkBase).send('사망중에는 이동할 수 없습니다.\n')
            return False
        #######################

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

        current_map.broadcast('%s가 %s쪽으로 갑니다.\n' % (self.get_owner_name_title(), dest))
        self.get_component(GocNetworkBase).broadcast_in_map(
            '%s가 왔습니다.\n' % self.get_owner_name_title())
        self.get_component(GocNetworkBase).send(dest + '쪽으로 갑니다.\n')
        self.output_current_map_desc()
        return True

    def leave_world(self) -> bool:
        teamAttribute: GocTeamAttribute = self.get_component(GocTeamAttribute)
        if not teamAttribute.is_player:
            return False

        self.leave_map()
        entity: GocEntity = self.get_component(GocEntity)
        entity.destroy()

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
        status_desc = self.get_owner_name_title() + '\n'
        status_desc += entity.get_status_desc()
        status_desc += attribute.get_status_desc()

        self.get_component(GocNetworkBase).send(status_desc)

    def output_command_prompt(self):
        team_attribute: GocTeamAttribute = self.get_component(GocTeamAttribute)
        attribute: GocAttribute = self.get_component(GocAttribute)
        if not team_attribute.is_player():
            return

        command_prompt = '[%d/%d] ' % (attribute.hp, attribute.max_hp)
        self.get_component(GocNetworkBase).send(command_prompt)

    def output_help_msg(self):
        network_base: GocNetworkBase = self.get_component(GocNetworkBase)
        network_base.send(global_define.help_msg)