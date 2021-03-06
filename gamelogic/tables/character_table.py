#character_table.py
from __future__ import annotations

class CharacterInfo:
    def __init__(self, name: str, gain_xp: int,
         max_hp: int, atk: int, armor: int, spd: int,
         reward_item_id: int, reward_probability: int):
        self.name = name
        self.gain_xp = gain_xp
        self.max_hp = max_hp
        self.atk = atk
        self.armor = armor
        self.spd = spd
        self.reward_item_id = reward_item_id
        self.reward_probability = reward_probability

class CharacterTable:
    '''
    캐릭터들의 속성 정보를 가지고 있는 테이블 클래스
    '''
    __global_instance: 'CharacterTable' = None

    @classmethod
    def get_chr_info(cls, lv: int) -> CharacterInfo:
        return cls.__global_instance.get_row(lv)

    @classmethod
    def initialize(cls) -> CharacterTable:
        instance = CharacterTable()
        cls.__global_instance = instance
        return instance
    
    @classmethod
    def deinitialize(cls):
        cls.__global_instance = None

    @classmethod
    def instance(cls):
        return cls.__global_instance

    def __init__(self):
        self._table = {}

    def init_test(self):
        self.add_row(100000, '경비병', 10, 100, 10, 1, 1, 0, 100)
        self.add_row(100001, '경비대장', 100, 150, 11, 1, 1, 0, 100)

    def add_row(self,\
     id: int, name: str, gain_xp: int, max_hp: int,\
     atk: int, armor: int, spd: int, reward_item_id: int, reward_probability: int) -> bool:
        chr_info = CharacterInfo(name, gain_xp, max_hp, atk, armor, spd, reward_item_id, reward_probability)

        if id in self._table:
            return False

        self._table[id] = chr_info
        return True

    def get_row(self, lv: int) -> CharacterInfo:
        if lv not in self._table:
            return None

        return self._table[lv]
