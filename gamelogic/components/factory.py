
'''
factory.py

instance를 생성하는 함수들
'''
from .gameobject import GameObject
from .behaviour import GocBehaviour
from .attribute import GocAttribute
from .team_attribute import GocTeamAttribute
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

def create_object_base(\
     name: str, is_player: bool, id: int, team_index: int) -> GameObject:
    '''공통 컴포넌트들을 가지고 있는 GameObject를 생성하는 함수.'''
    obj = GameObject(name, id)
    obj.add_component(GocEntity)
    obj.add_component(GocAttribute)
    obj.add_component(GocTeamAttribute, is_player, team_index)
    obj.add_component(GocBehaviour)
    obj.add_component_with_key(GocUpdaterBase, GocUpdater)
    return obj

def create_object_player(name: str, id: int, lv: int, xp: int) -> GameObject:
    '''player GameObject를 생성하는 함수'''
    obj = create_object_base(name, True, id, 0)
    obj.add_component_with_key(GocNetworkBase, GocNetwork)
    
    attribute: GocAttribute = obj.get_component(GocAttribute)
    attribute.set_attribute(lv, xp)
    attribute.set_hp_full()
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

def create_console_object(name: str, event: NetworkConsoleEventBase, lv: int, xp: int) -> GameObject:
    '''console player object를 생성하는 함수'''
    assert(isinstance(event, NetworkConsoleEventBase))
    obj = create_object_base(name, True, CONSOLE_PLAYER_ID, 0)
    obj.add_component_with_key(GocNetworkBase, GocNetworkConsole, event)

    attribute: GocAttribute = obj.get_component(GocAttribute)
    attribute.set_attribute(lv, xp)
    attribute.set_hp_full()
    return obj

    