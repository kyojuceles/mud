# map.py

import weakref
from ..utils import instance_checker

class Map:
    """
    방 하나를 담당하는 클래스
    """
    
    def __init__(self, id, name = '', desc = ''):
        self._id = id
        self._visitable_maps = weakref.WeakValueDictionary()
        self._name = name
        self._desc = desc
        self._objs = []

    def get_id(self):
        return self._id
        
    def get_name(self):
        return self._name
    
    def get_desc(self):
        output_string = self.get_name()
        output_string += '\n'
        output_string += self._desc
        output_string += '\n'

        visitable_map = self._visitable_maps.keys()
        output_string += '['
        output_string += '.'.join(visitable_map)
        output_string += ']\n'

        for obj in self._objs:
            output_string += obj.get_component('GocEntity').get_desc()

        return output_string

    def add_visitable_map(self, dest, map):
        assert(instance_checker.is_map(map))
        if dest in self._visitable_maps:
            return False

        self._visitable_maps[dest] = map
        return True

    def get_visitable_map(self, dest):
        if dest not in self._visitable_maps:
            return None

        return self._visitable_maps[dest]

    def get_visitable_map_list(self):
        return [(item[0], item[1].get_id()) for item in self._visitable_maps.items()]
            
    def update(self):
        pass

    def enter_map(self, obj):
        if obj in self._objs:
            return False

        self._objs.append(obj)
        self._objs.sort(key = lambda obj : obj.get_name())
        return True

    def leave_map(self, obj):
        if obj not in self._objs:
            return False

        self._objs.remove(obj)
        self._objs.sort(key = lambda obj : obj.get_name())
        return True

    def get_object(self, name):
        '''
        이름으로 오브젝트를 얻어온다.
        만약 앞에 숫자. 형태가 나오면 숫자 순서에 있는 오브젝트를 얻어온다.
        예) '1.병사' -> 첫번째 '병사', '2.병사' -> 두번째 '병사'
        '''
        words = name.split('.')
        order = 0
        key = name
        if len(words) > 1 and words[0].isdigit():
            order = int(words[0]) - 1
            key = words[1]
        obj_list = [obj for obj in self._objs if obj.get_name() == key]
        if order >= len(obj_list):
            return None
        
        return obj_list[order]

    def get_object_list(self):
        return tuple(self._objs)



        


    

    