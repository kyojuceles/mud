import time
import gamelogic.global_define as global_define
from gamelogic.client_info import ClientInfo
from gamelogic.processor import GameLogicProcessor
from gamelogic.global_instance import GameLogicProcessorEvent
from gamelogic.components import factory
from gamelogic.components.network import NetworkConsoleEventBase
from gamelogic.utils import async_input


class EventProcessor(GameLogicProcessorEvent):

    def event_output(self, output):
        print('[SYSTEM] ' + output, end = '')

class EventNetworkConsole(NetworkConsoleEventBase):

    def on_receive(self, msg):
        print(msg, end = '')

game_logic_processor = GameLogicProcessor(EventProcessor(), EventNetworkConsole())
game_logic_processor.init_test()
game_logic_processor.start()
client_info_list = []
current_client_info_index = -1

def get_current_client_info():
    global client_info_list
    global current_client_info_index

    if not client_info_list:
        return None

    return client_info_list[current_client_info_index]

def console_command_process(command):
    global client_info_list
    global current_client_info_index

    if command == '종료':
        return False

    client_count = len(client_info_list)
    if command == '접속':
        new_client_info = ClientInfo(True)
        new_client_info.set_status(ClientInfo.STATUS_NOT_LOGIN)
        client_info_list.append(new_client_info)
        client_count += 1
        current_client_info_index = client_count - 1
        game_logic_processor.get_event().event_output('이름을 입력해주세요.\n')
        return True

    client_info = client_info_list[current_client_info_index]
    if client_info is None:
        return True

    if command == '캐릭터교체' and client_info.get_status() == ClientInfo.STATUS_LOGIN:
        current_client_info_index += 1
        if current_client_info_index >= client_count:
            current_client_info_index = 0

        game_logic_processor.get_event().event_output(\
            '%s로 캐릭터를 교체합니다.\n' % get_current_client_info().get_player().get_name())        
        return True
    
    game_logic_processor.dispatch_message(client_info, command)
    return True

while(True):
    is_exit = False
    results = async_input.read()
    for result in results:
        if not console_command_process(result):
            is_exit = True
            break
    
    if is_exit:
        break

    game_logic_processor.update()
    time.sleep(0.00001)

game_logic_processor.get_event().event_output('프로그램을 종료합니다.\n')

#테스트