#skill.py

import gamelogic.global_define as global_define
from .gameobject import GameObject
from .gameobject import Component
from .network import GocNetworkBase
from .attribute import GocAttribute
from .behaviour import GocBehaviour

class GocSkill(Component):
    '''스킬 보유하고 사용을 처리하는 컴포넌트'''
    def __init__(self):
        super().__init__()
        self._skill_list = {}

    def init_test(self):
        self.add_skill(Skill('힐', Skill.TYPE_RECOVERY_HP, 100, 10, 2))

    def add_skill(self, skill: 'Skill') -> bool:
        if skill.get_name() in self._skill_list:
            return False

        self._skill_list[skill.get_name()] = skill
        return True

    def use_skill(self, skill_name: str, target_name: str = ''):
        target: GameObject = None

        if target_name == '':
            target = self.get_owner()

        #스킬을 가지고 있는지 체크
        if skill_name not in self._skill_list:
            self.get_component(GocNetworkBase).send(global_define.use_skill_not_exist)
            return False

        skill: Skill = self._skill_list[skill_name]
        attribute: GocAttribute = self.get_component(GocAttribute)

        #skill cool time이 남았는지 체크
        if skill.is_remain_cool_time():
            self.get_component(GocNetworkBase).send(global_define.use_skill_cool_time)
            return False

        #sp가 충분한지 체크
        if attribute.sp < skill.get_cost():
            self.get_component(GocNetworkBase).send(global_define.use_skill_sp_is_not_enough)
            return False

        result = skill.use(target)

        #sp 차감(스킬 사용이 성공했을때만)
        if result:
            attribute.set_sp(attribute.sp - skill.get_cost())
            if self.get_owner() == target:
                self.get_component(GocNetworkBase).send('당신에게 %s를 사용합니다.\n' % skill.get_name())
            else:
                self.get_component(GocNetworkBase).send('%s에게 %s를 사용합니다.\n' %\
                 (target.get_name(), skill.get_name()))
        
        return result

    def reduce_cool_time(self):
        for skill in self._skill_list.values():
            skill.reduce_cool_time()

    def output_skill_list(self):
        network_base: GocNetworkBase = self.get_component(GocNetworkBase)
        network_base.send('[스킬리스트]\n')
        for skill_name in self._skill_list.keys():
            network_base.send(skill_name + '\n')

class Skill:
    TYPE_RECOVERY_HP: int = 1

    '''스킬 효과를 처리하는 클래스'''
    def __init__(self, skill_name: str, effect_type: int, effect_arg: int, cost_sp: int, cool_time: int):
        self._name = skill_name
        self._effect_type = effect_type
        self._effect_arg = effect_arg
        self._cost_sp = cost_sp
        self._cool_time = cool_time
        self._remain_cool_time = 0

    def use(self, target: GameObject):
        #힐 효과 처리
        if self._effect_type == Skill.TYPE_RECOVERY_HP:
            if target is None:
                return False
            behaviour: GocBehaviour = target.get_component(GocBehaviour)
            behaviour.recovery(self._effect_arg)
            self._remain_cool_time = self._cool_time            
            return True

        return False

    def is_remain_cool_time(self):
        return True if self._remain_cool_time > 0 else False

    def reduce_cool_time(self):
        self._remain_cool_time = max(0, self._remain_cool_time - 1)

    def get_name(self):
        return self._name
    
    def get_cost(self):
        return self._cost_sp
