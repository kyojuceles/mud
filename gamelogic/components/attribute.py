#attribyte.py
from .gameobject import Component
from .entity import GocEntity
from ..tables.level_table import LevelTable

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
            max_hp: int, hp: int,
            atk: int, armor:int , spd: int):
        self.max_hp = max_hp
        self.hp = hp
        self.atk = atk
        self.armor = armor
        self.spd = spd
        self.set_level(lv)
        self.xp = xp

    def set_level(self, lv: int):
        self.lv = lv
        self.next_xp = 0
        
        entity: GocEntity = self.get_component(GocEntity)
        if entity.is_player():
            level_info = LevelTable.get_lv_info(lv)
            if level_info is not None:
                self.next_xp = level_info.next_xp

    def is_can_level_up(self):
        return self.next_xp > 0

    def is_die(self):
        return self.hp <= 0

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
        if self.xp >= next_xp and self.is_can_level_up():
            self.set_level(self.lv + 1)
            return True
        return False
