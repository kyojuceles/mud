import time
from gamelogic.processor import GameLogicProcessor
from gamelogic.processor import GameLogicProcessorEvent
from gamelogic.components import factory
from gamelogic.command_dispatcher import CommandDispatcher
from gamelogic.utils import async_input


class EventProcessor(GameLogicProcessorEvent):

    def event_output(self, output):
        print(output)

game_logic_processor = GameLogicProcessor(EventProcessor())
dispatcher = CommandDispatcher(game_logic_processor)
dispatcher.init_test()
game_logic_processor.start()

def console_command_process(command):
    if command == '종료':
        return False
    
    dispatcher.dispatch(0, result)
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

    time.sleep(0.00001)

GameLogicProcessor.get_event_instance().event_output('프로그램을 종료합니다.')