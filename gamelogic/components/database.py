#database.py

import db.db_processor_mysql as db_processor
from .gameobject import Component
from .attribute import GocAttribute


class GocDatabase(Component):
    '''database관련 처리를 담당하는 컴포넌트'''
    def __init__(self):
        super().__init__()

    async def update_level_and_xp(self) -> bool:
        attribute: GocAttribute = self.get_component(GocAttribute)
        result = await db_processor.update_level_and_xp(self.get_owner_name(), attribute.lv, attribute.xp)
        return result

    async def update_hp(self) -> bool:
        attribute: GocAttribute = self.get_component(GocAttribute)
        result = await db_processor.update_hp(self.get_owner_name(), attribute.hp)
        return result
