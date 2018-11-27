#inventory.py

from .gameobject import Component
from ..item.item import Item

class GocInventory(Component):
    '''
    캐릭터의 아이템을 관리하는 컴포넌트
    획득, 파괴, 사용, 장착, 해제 등의 기능을 담당한다.
    '''
    def __init__(self):
        super().__init__()
        self._items = []

    def add_item(self, item: Item):
        self._items.append(item)
        self._sort()

    def del_item(self, item: Item):
        if item not in self._items:
            return False
            
        self._items.remove(item)
        self._sort()
        return True

    def get_item_list(self):
        return tuple(self._items)

    def _sort(self):
        self._items.sort(key = lambda value : value.get_name())
