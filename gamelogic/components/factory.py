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

def create_object_base(
    name: str, id: int, hp: int, atk: int, armor: int, spd: int) -> GameObject:
    obj = GameObject(name, id)
    obj.add_component(GocEntity)
    obj.add_component(GocAttribute, hp, atk, armor, spd)
    obj.add_component(GocBehaviour)
    obj.add_component_with_key(GocUpdaterBase, GocUpdater)

    return obj

def create_object_player(
    name: str, id: int, hp: int, atk: int, armor: int, spd: int) -> GameObject:
    obj = create_object_base(name, id, hp, atk, armor, spd)
    obj.add_component_with_key(GocNetworkBase, GocNetwork)
    return obj

def create_object_npc(
    name: str, id: int, hp: int, atk: int, armor: int, spd: int) -> GameObject:
    obj = create_object_base(name, id, hp, atk, armor, spd)
    obj.add_component_with_key(GocNetworkBase, GocNetworkPass)
    return obj

def create_console_object(
    name: str, event: NetworkConsoleEventBase, 
    hp: int, atk: int, armor: int, spd: int) -> GameObject:
    assert(isinstance(event, NetworkConsoleEventBase))
    obj = create_object_base(name, -1, hp, atk, armor, spd)
    obj.add_component_with_key(GocNetworkBase, GocNetworkConsole, event)
    return obj

    