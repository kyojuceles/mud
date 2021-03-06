#level_table.py
from __future__ import annotations

class LevelInfo:
    def __init__(self, next_xp: int, max_hp: int, max_sp: int, atk: int, armor: int, spd: int):
        self.next_xp = next_xp
        self.max_hp = max_hp
        self.max_sp = max_sp
        self.atk = atk
        self.armor = armor
        self.spd = spd

class LevelTable:
    '''
    레벨 정보를 가지고 있는 테이블 클래스
    '''
    __global_instance: 'LevelTable' = None

    @classmethod
    def get_lv_info(cls, lv: int) -> LevelInfo:
        return cls.__global_instance.get_row(lv)

    @classmethod
    def get_max_level(cls) -> int:
        return cls.__global_instance.get_max_level_()

    @classmethod
    def initialize(cls) -> LevelTable:
        instance = LevelTable()
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
        self._max_level = 0

    def init_test(self):
        self.add_row(1, 100, 150, 20, 10, 2, 1)
        self.add_row(2, 200, 300, 30, 12, 2, 1)
        self.add_row(3, 300, 450, 40, 14, 3, 1)
        self.add_row(4, 400, 600, 50, 16, 3, 1)
        self.add_row(5, 500, 750, 60, 18, 3, 1)
        self.set_max_level(5)

    def add_row(self,\
     lv: int, next_xp: int, max_hp: int, max_sp: int,\
     atk: int, armor: int, spd: int) -> bool:
        lv_info = LevelInfo(next_xp, max_hp, max_sp, atk, armor, spd)

        if lv in self._table:
            return False

        self._table[lv] = lv_info
        return True

    def get_row(self, lv: int) -> LevelInfo:
        if lv not in self._table:
            return None

        return self._table[lv]

    def set_max_level(self, max_lv: int):
        self._max_level = max_lv

    def get_max_level_(self) -> int:
        return self._max_level

