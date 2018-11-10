# 주기적으로 update가 호출되는 component

from ..global_instance import GlobalInstance
from .gameobject import Component

class GocUpdater(Component):
    name = 'GocUpdater'

    def update(self):
        pass
        entity = self.get_component('GocEntity')
        if entity is None:
            return


