
from .gameobject import Component

'''
updater_base.py

updater components들의 부모 클래스
'''

class GocUpdaterBase(Component):
    
    def update(self):
        raise NotImplementedError('you should implement update method')
