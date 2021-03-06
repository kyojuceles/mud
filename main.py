import time
import sys
import asyncio
import platform
import db.db_processor_mysql as db_processor
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
        self._is_start = False
        global_define.load_ini('config.ini')

    def start(self, listen_addr: str, listen_port: int) -> bool:
        loop = asyncio.get_event_loop()
        self._loop = loop

        self.event_output('DB server에 접속합니다.\n')
        if not db_processor.connect_db_server(\
                    global_define.DATABASE_HOST,\
                    global_define.DATABASE_USER,\
                    global_define.DATABASE_PASSWORD,\
                    global_define.DATABASE_NAME, loop):
            return False
        self.event_output('DB server에 접속했습니다.\n')

        db_processor.set_log_handler(self.event_output)
        self._game_logic_processor = GameLogicProcessor(self)
        self._game_logic_processor.initialize()        
        self._connection_manager = ConnectionManager(self)     
        self._game_logic_processor.init_test()
        self._game_logic_processor.start()
        self._connection_manager.start_server(listen_addr, listen_port, loop)
        listen_addr = self._connection_manager.get_listen_addr()
        listen_port = self._connection_manager.get_listen_port()
        self._game_logic_processor.get_event().event_output('접속을 받기 시작합니다. (%s:%d)\n' % (listen_addr, listen_port))
        self._tasks = [asyncio.ensure_future(self._update()),\
                        asyncio.ensure_future(self._input_process())]
        self._is_start = True
        return True

    def loop(self):
        self._loop.run_until_complete(asyncio.gather(*self._tasks))

    def stop(self):
        if not self._is_start:
            return

        self._connection_manager.close()
        self._game_logic_processor.deinitialize()
        self._game_logic_processor = None
        self._connection_manager = None
        db_processor.close()

    async def _input_process(self):
        while True:
            results = []
            if platform.system() != 'Windows':
                results = async_input.read()
                await asyncio.sleep(0.00001)
            else:
                results = await async_input.async_read() 
            
            for result in results:
                await self._console_command_process(result)

    async def _update(self):
        while True:
            await self._game_logic_processor.update()
            await asyncio.sleep(0.00001)
    
    async def _console_command_process(self, command):
        if command == '종료':
            return False

        if command == '접속':
            self._local_client_info = ClientInfo(None, self.on_console_disconnect)
            self._game_logic_processor.output_login_name_message(self._local_client_info)
            return True

        if self._local_client_info is None:
            return True

        await self._game_logic_processor.dispatch_message(self._local_client_info, command)
        return True

    def event_output(self, output):
        print('[SYSTEM] ' + str(output), end = '')

    async def on_connect(self, connection: 'Connection'):
        '''새로운 접속이 발생했을때의 처리'''
        client_info = ClientInfo(connection.send, connection.disconnect, connection.set_echo_mode)
        connection.set_extra_data(client_info)
        self._game_logic_processor.output_login_name_message(client_info)

    async def on_recv(self, connection: 'Connection', msg: str):
        '''peer로 부터 메시지가 도착했을때의 처리'''
        client_info: ClientInfo = connection.get_extra_data()
        await self._game_logic_processor.dispatch_message(client_info, msg)

    async def on_disconnect(self, connection: 'Connection'):
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
if mud_server.start('127.0.0.1', global_define.SERVER_LISTEN_PORT):
    mud_server.loop()
else:
    mud_server.event_output('DB Server 접속이 실패했습니다.\n')

mud_server.stop()