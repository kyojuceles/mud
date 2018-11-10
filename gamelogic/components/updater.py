# 주기적으로 update가 호출되는 component

from ..global_instance import GlobalInstance
from .gameobject import Component
from .entity import GocEntity

class GocUpdater(Component):
    name = 'GocUpdater'

    def update(self):
        entity = self.get_component('GocEntity')
        if entity is None:
            return

        status = entity.get_status()
        if status == GocEntity.STATUS_BATTLE:
            self._status_battle_update()

    def _status_battle_update(self):
        entity = self.get_component('GocEntity')
        target = entity.get_target()

        #타겟이 존재하지 않거나 사망상태이면 전투를 종료한다.
        if target is None:
            entity.set_status(GocEntity.STATUS_IDLE)
            return

        target_entity = target.get_component('GocEntity')
        if target_entity.get_status() == GocEntity.STATUS_DEATH:
            entity.set_status(GocEntity.STATUS_IDLE)
            entity.set_target(None)
            return
        
        behaviour = self.get_component('GocBehaviour')
        behaviour.attack(target)

        #사망처리
        target_attribute = target.get_component('GocAttribute')
        if target_attribute.is_die():
            GlobalInstance.get_event().event_output('%s는 사망했다.\n' % target.get_name())
            target_entity.set_status(GocEntity.STATUS_DEATH)
            target_entity.set_target(None)
            entity.set_status(GocEntity.STATUS_IDLE)
            entity.set_target(None)
        

        
            
            
            



