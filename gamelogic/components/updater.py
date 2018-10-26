# 주기적으로 update가 호출되는 component

from ..global_instance import GlobalInstance
from .gameobject import Component

class GocUpdater(Component):
    name = 'GocUpdater'

    def update(self):
        GlobalInstance.get_event()\
        .event_output('call %s\'s update()' % self.get_owner_name())

