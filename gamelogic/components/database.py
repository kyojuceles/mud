#database.py

import db.db_processor_mysql as db_processor
from .gameobject import Component
from .attribute import GocAttribute
from .inventory import GocInventory
from ..item.item import Item


class GocDatabase(Component):
    '''database관련 처리를 담당하는 컴포넌트'''
    def __init__(self, player_uid: int):
        super().__init__()
        self._player_uid = player_uid

    async def update_level_and_xp(self) -> bool:
        attribute: GocAttribute = self.get_component(GocAttribute)
        result = await db_processor.update_level_and_xp(self.get_owner_name(), attribute.lv, attribute.xp)
        return result

    async def update_hp(self) -> bool:
        attribute: GocAttribute = self.get_component(GocAttribute)
        result = await db_processor.update_hp(self.get_owner_name(), attribute.hp)
        return result

    async def get_item_list(self) -> bool:
        datas, ret = await db_processor.get_item_list(self._player_uid)

        if not ret:
            return False

        #가지고 온 리스트를 기반으로 아이템을 생성해서 인벤토리에 넣는다.
        from . import factory
        inventory: GocInventory = self.get_component(GocInventory)
        for data in datas:
            uid = data[0]
            item_id = data[1]
            item = factory.create_item(uid, item_id)
            if item is not None:
                inventory.add_item(item)

        return True


        
