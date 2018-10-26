#command_dispatcher.py

from .global_instance import GlobalInstance
from .components import factory

class CommandDispatcher:

    arg_infos_list = {}

    def __init__(self):
        self._player = None

    def get_player(self, index):
        return self._player

    def dispatch(self, index, input_string):
        ret, cmd, args = self._cmd_parse(input_string)

        if not ret:
            GlobalInstance.get_event().event_output('명령어가 올바르지 않습니다.')
            return True

        if cmd == '종료':
            return False

        if cmd == '접속':
            player = factory.create_object('플레이어', 100, 10, 1, 1)
            world = GlobalInstance.get_world().get_world()
            world.add_player(player)
            self._player = player
            return True

        if cmd in ['남', '북']:
            if self._player is not None:
                behaviour = self._player.get_component('GocBehaviour')
                behaviour.visit_map(cmd)
            return True

        GlobalInstance.get_event().event_output('명령어가 존재하지 않습니다.')        
        return True

    def _cmd_parse(self, input_string):
        """
        입력받은 input_string을 파싱해서 형식에 맞는 cmd와 args를 리턴한다.
        input_string이 적절하지 않으면 False를 리턴한다.
        """
        assert(isinstance(input_string, str))

        cmd, result_string = self._pop_word(input_string)

        if cmd == '':
            return False, '', ()
 
        arg_infos = []
        if cmd in self.arg_infos_list:
            arg_infos = self.arg_infos_list[cmd]

        ret, args = self._arg_parse(result_string, arg_infos)
        return ret, cmd, args

    def _arg_parse(self, arg_string, arg_infos):
        '''arg_infos를 기반으로 arg_string을 파싱하여 인자를 리턴한다.'''
        assert(isinstance(arg_string, str))
        assert(isinstance(arg_infos, list))

        args = []

        for arg_info in arg_infos:
            if arg_info == 'msg':
                args.append(arg_string.lstrip())
                break
            
            arg_str, arg_string = self._pop_word(arg_string)
            
            if arg_info == 'int':
                if not arg_str.isdigit():
                    return False, ()
                args.append(int(arg_str))
            else:
                args.append(arg_str)

        return True, tuple(args)
    
    def _pop_word(self, input_string):
        '''명령의 첫번째 단어와 이를 제외한 문장을 리턴한다.'''
        lstrip_string = input_string.lstrip()
        left_index = lstrip_string.find(' ')

        if left_index != -1:
            word = lstrip_string[:left_index]
            result_string = lstrip_string[left_index:]
        else:
            word = lstrip_string
            result_string = ''

        return word, result_string
