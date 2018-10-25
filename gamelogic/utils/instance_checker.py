# 인스턴트가 올바른지 체크하는 모듈들
from ..components.gameobject import GameObject
from ..world.map import Map

def is_gameobject(obj):
    return isinstance(obj, GameObject)

def is_player(obj):
    if not isinstance(obj, GameObject):
        return False
    return True

def is_npc(obj):
    if not isinstance(obj, GameObject):
        return False
    return True

def is_map(obj):
    if not isinstance(obj, Map):
        return False
    return True


