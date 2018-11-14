
'''
factory.py

instance를 생성하는 함수들
'''
from .gameobject import GameObject
from .behaviour import GocBehaviour
from .attribute import GocAttribute
from .updater_base import GocUpdaterBase
from .updater import GocUpdater
from .entity import GocEntity
from .network import GocNetworkBase
from .network import GocNetwork
from .network import GocNetworkConsole
from .network import GocNetworkPass
from .network import NetworkConsoleEventBase
from ..tables.character_table import CharacterTable
from ..tables.level_table import LevelTable

CONSOLE_PLAYER_ID = -1

def create_object_base(
     name: str, is_player: bool, lv: int, xp: int, id: int,
     hp: int, atk: int, armor: int, spd: int) -> GameObject:
    '''공통 컴포넌트들을 가지고 있는 GameObject를 생성하는 함수.'''
    obj = GameObject(name, id)
    obj.add_component(GocEntity, is_player)
    attribute: GocAttribute = obj.add_component(GocAttribute)
    obj.add_component(GocBehaviour)
    obj.add_component_with_key(GocUpdaterBase, GocUpdater)
    
    attribute.set_attribute(lv, xp, hp, hp, atk, armor, spd)
    return obj

def create_object_player(
     name: str, lv: int, xp: int,
     id: int, hp: int, atk: int, armor: int, spd: int) -> GameObject:
    '''player GameObject를 생성하는 함수'''
    obj = create_object_base(name, True, lv, xp, id, hp, atk, armor, spd)
    obj.add_component_with_key(GocNetworkBase, GocNetwork)
    return obj

def create_object_npc_with_attribute(
     name: str, id: int,
     hp: int, atk: int, armor: int, spd: int) -> GameObject:
    '''npc GameObject를 능력치를 지정하여 생성하는 함수'''
    obj = create_object_base(name, False, 1, 0, id, hp, atk, armor, spd)
    obj.add_component_with_key(GocNetworkBase, GocNetworkPass)
    return obj

def create_object_npc(id: int) -> GameObject:
    '''npc GameObject를 생성하는 함수'''
    chr_info = CharacterTable.get_chr_info(id)
    if chr_info is None:
        return None

    obj = create_object_base(chr_info.name, False, 1, 0, id,
            chr_info.max_hp, chr_info.atk,
            chr_info.armor, chr_info.spd)
    obj.add_component_with_key(GocNetworkBase, GocNetworkPass)
    return obj

def create_console_object(
     name: str, event: NetworkConsoleEventBase, 
     lv: int, xp: int, hp: int, atk: int, armor: int, spd: int) -> GameObject:
    '''console player object를 생성하는 함수'''
    assert(isinstance(event, NetworkConsoleEventBase))
    obj = create_object_base(name, True, lv, xp, CONSOLE_PLAYER_ID, hp, atk, armor, spd)
    obj.add_component_with_key(GocNetworkBase, GocNetworkConsole, event)
    return obj

    