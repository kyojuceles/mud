import time
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

def console_command_process(command):
    if command == '종료':
        return False
    
    game_logic_processor.dispatch_message(GameLogicProcessor.CONSOLE_PLAYER_ID, command)
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