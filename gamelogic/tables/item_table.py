#character_table.py
from __future__ import annotations

class ItemInfo:
    def __init__(self, name: str):
        self.name = name

class ItemTable:
    '''
    캐릭터들의 속성 정보를 가지고 있는 테이블 클래스
    '''
    __global_instance: 'ItemTable' = None

    @classmethod
    def get_item_info(cls, item_id: int) -> ItemInfo:
        return cls.__global_instance.get_row(item_id)

    @classmethod
    def initialize(cls) -> ItemTable:
        instance = ItemTable()
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
        self.add_row(0, 'wooden_sword')
        self.add_row(1, 'wooden_armor')

    def add_row(self, id: int, name: str) -> bool:
        item_info = ItemInfo(name)

        if id in self._table:
            return False

        self._table[id] = item_info
        return True

    def get_row(self, lv: int) -> ItemInfo:
        if lv not in self._table:
            return None

        return self._table[lv]
