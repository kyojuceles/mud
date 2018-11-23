#updater.py
import db.db_processor_mysql as db_processor
from ..global_instance import GlobalInstance
from .updater_base import GocUpdaterBase
from .database import GocDatabase
from .attribute import GocAttribute
from .team_attribute import GocTeamAttribute
from .behaviour import GocBehaviour
from .entity import GocEntity
from .network import GocNetworkBase
from ..tables.character_table import CharacterTable

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

    def update_recovery(self):
        #최대 hp의 5프로가 회복된다.(임시)
        behaviour: GocBehaviour = self.get_component(GocBehaviour)
        network_base: GocNetworkBase = self.get_component(GocNetworkBase)
        behaviour.recovery_by_percent(5)
        network_base.send('\n')
        behaviour.output_command_prompt()

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
                gain_xp = CharacterTable.get_chr_info(target.get_id()).gain_xp
                is_level_up = attribute.gain_xp(gain_xp)
                self.get_component(GocNetworkBase).send('%d 경험치를 획득했습니다.\n' % gain_xp)
                # 레벨업 처리.
                if is_level_up:
                     self.get_component(GocNetworkBase).send('레벨이 상승했습니다. 축하합니다!\n')

                #db에서 레벨과 경험치를 업데이트 한다.
                await self.get_component(GocDatabase).update_level_and_xp()

        behaviour.output_command_prompt()


                
        

        
            
            
            



