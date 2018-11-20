import time
import sys
import asyncio
import gamelogic.global_define as global_define
from gamelogic.processor import GameLogicProcessor
from gamelogic.global_instance import GameLogicProcessorEvent
from gamelogic.components import factory
from gamelogic.components.behaviour import GocBehaviour
from gamelogic.utils import async_input
from gamelogic.client_info import ClientInfo
from network.network import ConnectionManager
from network.network import Connection
from network.network import ConnectionManagerEventBase

class MudServer(GameLogicProcessorEvent, ConnectionManagerEventBase):
    def __init__(self):
        self._game_logic_processor: GameLogicProcessor = None
        self._connection_manager: ConnectionManager = None
        self._loop = None
        self._tasks = None
        self._local_client_info = None

    def start(self, listen_addr: str, listen_port: int):
        self._game_logic_processor = GameLogicProcessor(self)        
        self._connection_manager = ConnectionManager(self)        
        self._game_logic_processor.init_test()
        self._game_logic_processor.start()
        self._loop = self._connection_manager.start_server('127.0.0.1', 8888)
        listen_addr = self._connection_manager.get_listen_addr()
        listen_port = self._connection_manager.get_listen_port()
        self._game_logic_processor.get_event().event_output('접속을 받기 시작합니다. (%s:%d)\n' % (listen_addr, listen_port))
        self._tasks = [asyncio.ensure_future(self._update())]

    def loop(self):
        self._loop.run_until_complete(asyncio.gather(*self._tasks))

    def stop(self):
        self._connection_manager.close()
        self._game_logic_processor = None
        self._connection_manager = None
        
    async def _update(self):
        while True:
            results = async_input.read()
            for result in results:
                self._console_command_process(result) 
            self._game_logic_processor.update()
            await asyncio.sleep(0.00001)
    
    def _console_command_process(self, command):
        if command == '종료':
            return False

        if command == '접속':
            self._local_client_info = ClientInfo(None, self.on_console_disconnect)
            self._game_logic_processor.output_welcome_message(self._local_client_info)
            return True

        if self._local_client_info is None:
            return True

        self._game_logic_processor.dispatch_message(self._local_client_info, command)
        return True

    def event_output(self, output):
        print('[SYSTEM] ' + output, end = '')

    def on_connect(self, connection: 'Connection'):
        '''새로운 접속이 발생했을때의 처리'''
        client_info = ClientInfo(connection.send, connection.disconnect)
        connection.set_extra_data(client_info)
        self._game_logic_processor.output_welcome_message(client_info)

    def on_recv(self, connection: 'Connection', msg: str):
        '''peer로 부터 메시지가 도착했을때의 처리'''
        client_info: ClientInfo = connection.get_extra_data()
        self._game_logic_processor.dispatch_message(client_info, msg)

    def on_disconnect(self, connection: 'Connection'):
        '''접속이 끊겼을때의 처리'''
        client_info: ClientInfo = connection.get_extra_data()
        player = client_info.get_player()
        if player:
            player.get_component(GocBehaviour).leave_world()
        client_info.deinitialize()

    def on_console_disconnect(self):
        '''콘솔 플레이어가 나가기를 했을때의 처리'''
        player = self._local_client_info.get_player()
        if player:
            player.get_component(GocBehaviour).leave_world()
            self._local_client_info.send('접속이 종료되었습니다.\n')
        self._local_client_info.deinitialize()
        self._local_client_info = None

mud_server = MudServer()
mud_server.start('127.0.0.1', 8888)
mud_server.loop()
mud_server.stop()