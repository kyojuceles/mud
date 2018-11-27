
'''
factory.py

instance를 생성하는 함수들
'''
import gamelogic.global_define as global_define
from .gameobject import GameObject
from .behaviour import GocBehaviour
from .attribute import GocAttribute
from .database import GocDatabase
from .team_attribute import GocTeamAttribute
from .updater_base import GocUpdaterBase
from .updater import GocUpdater
from .entity import GocEntity
from .network import GocNetworkBase
from .network import GocNetwork
from .network import GocNetworkPass
from .inventory import GocInventory
from ..item.item import Item
from ..tables.character_table import CharacterTable
from ..tables.level_table import LevelTable
from ..tables.item_table import ItemTable

def create_object_base(\
     name: str, is_player: bool, id: int, team_index: int) -> GameObject:
    '''공통 컴포넌트들을 가지고 있는 GameObject를 생성하는 함수.'''
    obj = GameObject(name, id)
    obj.add_component(GocEntity)
    obj.add_component(GocAttribute)
    obj.add_component(GocTeamAttribute, is_player, team_index)
    obj.add_component(GocBehaviour)
    obj.add_component_with_key(GocUpdaterBase, GocUpdater)
    obj.add_component(GocInventory)
    return obj

def create_object_player(name: str, client_info, player_uid: int, lv: int, xp: int, hp: int) -> GameObject:
    '''player GameObject를 생성하는 함수'''
    obj = create_object_base(name, True, -1, 0)
    obj.add_component_with_key(GocNetworkBase, GocNetwork, client_info)
    obj.add_component(GocDatabase, player_uid)
    
    attribute: GocAttribute = obj.get_component(GocAttribute)
    attribute.set_attribute(lv, xp)
    if hp < 0:
        attribute.set_hp_full()
    else:
        attribute.set_hp(hp)
    return obj

def create_object_npc_with_attribute(\
     name: str, id: int,\
     hp: int, atk: int, armor: int, spd: int, team_index: int) -> GameObject:
    '''npc GameObject를 능력치를 지정하여 생성하는 함수'''
    obj = create_object_base(name, False, id, team_index)
    obj.add_component_with_key(GocNetworkBase, GocNetworkPass)

    attribute: GocAttribute = obj.get_component(GocAttribute)
    attribute.set_attribute(0, 0, hp, hp, atk, armor, spd)
    return obj

def create_object_npc(id: int) -> GameObject:
    '''npc GameObject를 생성하는 함수'''
    chr_info = CharacterTable.get_chr_info(id)
    if chr_info is None:
        return None

    obj = create_object_base(chr_info.name, False, id, 1)
    obj.add_component_with_key(GocNetworkBase, GocNetworkPass)

    attribute: GocAttribute = obj.get_component(GocAttribute)
    attribute.set_attribute(
         0, 0, chr_info.max_hp, chr_info.max_hp,
         chr_info.atk, chr_info.armor, chr_info.spd)
    return obj

def create_item(uid: int, item_id: int) -> Item:
    '''Item을 생성하는 함수'''
    item_info = ItemTable.get_item_info(item_id)
    if item_info is None:
        return None

    item = Item(uid, item_id, item_info.name)
    return item