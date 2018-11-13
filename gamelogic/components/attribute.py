from .gameobject import Component

class GocAttribute(Component):
    name = 'GocAttribute'

    def __init__(self, hp, atk, armor, spd):
        self.set_attribute(hp, hp, atk, armor, spd)

    def set_attribute(self, max_hp, hp, atk, armor, spd):
        self.max_hp = max_hp
        self.hp = hp
        self.atk = atk
        self.armor = armor
        self.spd = spd

    def is_die(self):
        return self.hp <= 0

    def get_status_desc(self):
        desc = ''
        desc += '체력:\t %d/%d\n' % (self.max_hp, self.hp)
        desc += '공격력:\t %d\n' % self.atk
        desc += '방어력:\t %d\n' % self.armor
        desc += '속도:\t %d\n' % self.spd
        return desc
