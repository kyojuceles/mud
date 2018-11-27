#updater_base.py
from .gameobject import Component

class GocUpdaterBase(Component):
    '''
    updater components들의 부모 클래스
    '''  
    def __init__(self):
        pass

    async def update(self):
        raise NotImplementedError('you should implement update method')

    def update_recovery(self):
        raise NotImplementedError('you should implement update_recovery method')

    def update_death(self):
        raise NotImplementedError('you should implement update_death method')
