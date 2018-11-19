#team_attribute.py

from .gameobject import GameObject
from .gameobject import Component

class GocTeamAttribute(Component):
    '''
    객체의 진형과 관련된 기능을 담당하는 컴포넌트
    플레이어인지 npc인지 아군인지 적인지 등등을 판단하는 기능을 주로 한다.
    '''
    def __init__(self, is_player: bool, team_index: int):
        super().__init__() 
        self._is_player = is_player
        self._team_index = team_index

    def is_player(self) -> bool:
        return self._is_player

    def is_ally(self, target: GameObject) -> bool:
        target_team_attribute: GocTeamAttribute = target.get_component(GocTeamAttribute)
        return self._team_index == target_team_attribute._team_index

    def get_team_index(self) -> int:
        return self._team_index    

    