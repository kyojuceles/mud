#updater_base.py
from .gameobject import Component

class GocUpdaterBase(Component):
    '''
    updater components들의 부모 클래스
    '''  
    def update(self):
        raise NotImplementedError('you should implement update method')
