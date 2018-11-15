#attribyte.py
from .gameobject import Component
from ..tables.level_table import LevelTable
from .team_attribute import GocTeamAttribute

class GocAttribute(Component):
    '''
    캐릭터의 능력치를 나타내는 클래스
    '''
    def __init__(self):
        self.lv = 0
        self.xp = 0
        self.next_xp = 0
        self.hp = 0
        self.max_hp = 0
        self.atk = 0
        self.armor = 0
        self.spd = 0

    def set_attribute(
            self, lv: int, xp: int,
            max_hp: int = 0, hp: int = 0,
            atk: int = 0, armor:int = 0, spd: int = 0):
        self.max_hp = max_hp
        self.hp = hp
        self.atk = atk
        self.armor = armor
        self.spd = spd
        self.lv = lv
        self.xp = xp
        self.calculate()        

    def calculate(self):
        team_attribute: GocTeamAttribute = self.get_component(GocTeamAttribute)
        if team_attribute.is_player():
            level_info = LevelTable.get_lv_info(self.lv)
            self.max_hp = level_info.max_hp
            self.atk = level_info.atk
            self.armor = level_info.armor
            self.spd = level_info.spd
            self.next_xp = level_info.next_xp

    def is_die(self):
        return self.hp <= 0

    def level_up(self):
        self.lv += 1
        self.calculate()
        self.set_hp_full()

    def set_hp(self, hp: int):
        self.hp = max(0, hp)
        self.hp = min(self.max_hp, self.hp)

    def set_hp_full(self):
        self.hp = self.max_hp

    def get_status_desc(self):
        desc = '레벨:\t %d\t\t 경험치:\t%d/%d\n' % (self.lv, self.xp, self.next_xp)
        desc += '체력:\t %d/%d\n' % (self.hp, self.max_hp)
        desc += '공격력:\t %d\n' % self.atk
        desc += '방어력:\t %d\n' % self.armor
        desc += '속도:\t %d\n' % self.spd
        return desc

    def gain_xp(self, xp: int) -> bool:
        '''
        경험치를 얻는다.
        xp  : 얻을 경험치
        ret : 레벨업 유무
        '''
        self.xp += xp
        next_xp = LevelTable.get_lv_info(self.lv).next_xp
        if self.xp >= next_xp and self._is_can_level_up():
            self.level_up()
            return True

        return False

    def _is_can_level_up(self):
        return self.lv < LevelTable.get_max_level()