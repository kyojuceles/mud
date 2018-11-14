#attribyte.py
from .gameobject import Component

class GocAttribute(Component):
    '''
    캐릭터의 능력치를 나타내는 클래스
    '''
    def __init__(self, hp: int, atk: int, armor: int, spd: int):
        self.set_attribute(hp, hp, atk, armor, spd, 1, 0)

    def set_attribute(
            self, max_hp: int, hp: int,
            atk: int, armor:int , spd: int,
            lv: int, xp: int):
        self.max_hp = max_hp
        self.hp = hp
        self.atk = atk
        self.armor = armor
        self.spd = spd
        self.lv = lv
        self.xp = xp

    def is_die(self):
        return self.hp <= 0

    def get_status_desc(self):
        desc = ''
        desc += '체력:\t %d/%d\n' % (self.max_hp, self.hp)
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
        return False 
