from .gameobject import GameObject
from .attribute import GocAttribute
from .behaviour import GocBehaviour
from .updater import GocUpdater
from .entity import GocEntity

def create_object(name, hp, atk, armor, spd):
    obj = GameObject(name)
    obj.add_component(GocEntity)
    obj.add_component(GocAttribute, hp, atk, armor, spd)
    obj.add_component(GocBehaviour)
    obj.add_component(GocUpdater)

    return obj