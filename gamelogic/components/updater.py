#updater.py
from ..global_instance import GlobalInstance
from .updater_base import GocUpdaterBase
from .attribute import GocAttribute
from .behaviour import GocBehaviour
from .entity import GocEntity
from .network import GocNetworkBase
from ..tables.character_table import CharacterTable

class GocUpdater(GocUpdaterBase):
    '''
    주기적으로 처리해야 할 기능들을 담당하는 컴포넌트
    '''
    def update(self):
        entity: GocEntity = self.get_component(GocEntity)
        if entity is None:
            return

        status = entity.get_status()
        if status == GocEntity.STATUS_BATTLE:
            self._status_battle_update()

    def _status_battle_update(self):
        entity: GocEntity = self.get_component(GocEntity)
        target = entity.get_target()

        #타겟이 존재하지 않거나 사망상태이면 전투를 종료한다.
        if target is None:
            entity.set_status(GocEntity.STATUS_IDLE)
            return

        target_entity: GocEntity = target.get_component(GocEntity)
        if target_entity.get_status() == GocEntity.STATUS_DEATH:
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

            # 플레이어인 경우 경험치 획득.
            if entity.is_player:
                attribute: GocAttribute = self.get_component(GocAttribute)
                gain_xp = CharacterTable.get_chr_info(target.get_id()).gain_xp
                is_level_up = attribute.gain_xp(gain_xp)
                self.get_component(GocNetworkBase).send('%d 경험치를 획득했습니다.\n' % gain_xp)
                # 레벨업 처리.
                if is_level_up:
                     self.get_component(GocNetworkBase).send('레벨이 상승했습니다. 축하합니다!\n')


                
        

        
            
            
            



