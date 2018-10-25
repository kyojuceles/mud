# 주기적으로 update가 호출되는 component

from ..processor import GameLogicProcessor
from .gameobject import Component

class GocUpdater(Component):
    name = 'GocUpdater'

    def update(self):
        GameLogicProcessor.get_event_instance()\
        .event_output('call %s\'s update()' % self.get_owner_name())

