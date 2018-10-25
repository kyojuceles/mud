from .gameobject import Component

class GocAttribute(Component):
    name = 'GocAttribute'

    def __init__(self, hp, atk, armor, spd):
        self.set_attribute(hp, atk, armor, spd)

    def set_attribute(self, hp, atk, armor, spd):
        self.hp = hp
        self.atk = atk
        self.armor = armor
        self.spd = spd

    def is_die(self):
        return self.hp <= 0
