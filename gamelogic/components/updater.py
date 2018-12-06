#updater.py
import random
import db.db_processor_mysql as db_processor
from ..global_instance import GlobalInstance
from .updater_base import GocUpdaterBase
from .database import GocDatabase
from .attribute import GocAttribute
from .team_attribute import GocTeamAttribute
from .behaviour import GocBehaviour
from .entity import GocEntity
from .network import GocNetworkBase
from .skill import GocSkill
from ..tables.character_table import CharacterTable
from ..tables.item_table import ItemTable

class GocUpdater(GocUpdaterBase):
    '''
    주기적으로 처리해야 할 기능들을 담당하는 컴포넌트
    '''
    def __init__(self):
        super().__init__()

    async def update(self):
        entity: GocEntity = self.get_component(GocEntity)
        if entity is None:
            return

        status = entity.get_status()
        if status == GocEntity.STATUS_BATTLE:
            await self._status_battle_update()

        self._reset_update()

        self.get_component(GocSkill).reduce_cool_time()

    def update_recovery(self):
        entity: GocEntity = self.get_component(GocEntity)
        if entity.is_die():
            return

        behaviour: GocBehaviour = self.get_component(GocBehaviour)
        network_base: GocNetworkBase = self.get_component(GocNetworkBase)
        behaviour.recovery_by_percent(25)
        behaviour.recovery_sp_by_percent(25)
        network_base.send('\n')
        behaviour.output_command_prompt()

    def update_death(self):
        entity: GocEntity = self.get_component(GocEntity)
        team_attribute: GocTeamAttribute = self.get_component(GocTeamAttribute)
        if not entity.is_die():
            return

        # npc의 경우 시체가 사라지는 처리.
        if not team_attribute.is_player():
            behaviour: GocBehaviour = self.get_component(GocBehaviour)
            behaviour.leave_map(False)

    def _reset_update(self):
        '''매 턴마다 필요한 초기화를 하는 함수'''
        entity: GocEntity = self.get_component(GocEntity)
        entity.reset_flee()

    async def _status_battle_update(self):
        entity: GocEntity = self.get_component(GocEntity)
        target = entity.get_target()

        #타겟이 존재하지 않거나 사망상태이면 전투를 종료한다.
        if target is None:
            entity.set_status(GocEntity.STATUS_IDLE)
            return

        #타겟이 같은방에 있지 않으면 전투를 종료한다.
        target_entity: GocEntity = target.get_component(GocEntity)
        if target_entity.get_map() is not entity.get_map():
            entity.set_status(GocEntity.STATUS_IDLE)
            entity.set_target(None)
            return       

        #타겟이 사망했으면 전투를 종료한다.
        if target_entity.is_die():
            entity.set_status(GocEntity.STATUS_IDLE)
            entity.set_target(None)
            return
        
        behaviour: GocBehaviour = self.get_component(GocBehaviour)
        behaviour.attack(target)

        #사망처리
        target_attribute: GocEntity = target.get_component(GocAttribute)
        if target_attribute.is_die():
            self.get_component(GocNetworkBase).send('%s는 사망했다.\n' % target.get_name())
            target.get_component(GocNetworkBase).send('당신은 사망했습니다.\n')
            target_entity.set_status(GocEntity.STATUS_DEATH)
            target_entity.set_target(None)
            entity.set_status(GocEntity.STATUS_IDLE)
            entity.set_target(None)

            team_attribute: GocTeamAttribute = self.get_component(GocTeamAttribute)
            # 플레이어인 경우 경험치 획득.
            if team_attribute.is_player():
                attribute: GocAttribute = self.get_component(GocAttribute)
                target_chr_info = CharacterTable.get_chr_info(target.get_id())
                gain_xp = target_chr_info.gain_xp
                is_level_up = attribute.gain_xp(gain_xp)
                self.get_component(GocNetworkBase).send('%d 경험치를 획득했습니다.\n' % gain_xp)
                # 레벨업 처리.
                if is_level_up:
                     self.get_component(GocNetworkBase).send('레벨이 상승했습니다. 축하합니다!\n')

                #db에서 레벨과 경험치를 업데이트 한다.
                await self.get_component(GocDatabase).update_level_and_xp()

                #아이템 획득 처리.
                reward_item_id = target_chr_info.reward_item_id
                reward_probability = target_chr_info.reward_probability
                reward_item_info = ItemTable.get_item_info(reward_item_id)

                if reward_item_info is not None:
                    random_number = random.randrange(1, 100)
                    if random_number <= reward_probability:
                        ret = await self.get_component(GocDatabase).create_item(reward_item_id)
                        if ret:
                            self.get_component(GocNetworkBase).send('%s을 얻었습니다.\n' % reward_item_info.name)
                    
        behaviour.output_command_prompt()


                
        

        
            
            
            



