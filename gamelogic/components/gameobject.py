'''
GameObject
이름을 가지고 컨테이너를 담을 수 있는 클래스
'''
class GameObject:
    def __init__(self, name, id = -1):
        self._name = name
        self._id = id
        self._components = {}

    def add_component(self, cls, *args):
        assert(issubclass(cls, Component))
        component = cls(*args)
        component.set_owner(self)
        self._components[id(component.__class__.name)] = component
        return component

    def get_component(self, cls_name):
        return self._components.get(id(cls_name))

    def has_component(self, cls_name):
        return id(cls_name) in self._components

    def get_components(self):
        return self._components.values()

    def get_name(self):
        return self._name
    
    def get_id(self):
        return self._id


'''
Component
GameObject에 포함되어 기능을 수행하는 클래스.
자신을 소유자의 객체를 얻을 수 있고, 소유자가 가진 Component를 얻을 수 있다.
'''
class Component:
    name = 'Component'

    def __init__(self):
        self.owner = None

    def get_owner_name(self):
        return self.owner.get_name() if self.has_owner() else ''

    def set_owner(self, owner):
        self.owner = owner

    def get_owner(self):
        return self.owner

    def has_owner(self):
        return True if self.owner is not None else False

    def get_component(self, cls_name):
        return self.owner.get_component(cls_name) if self.has_owner() else None

    def has_component(self, cls_name):
        return self.owner.has_component(cls_name) if self.has_owner() else False
