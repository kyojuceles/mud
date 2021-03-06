#network.py
import sys
import asyncio

IAC: int = 255

class ConnectionManagerEventBase:
    '''ConnectionManager로 부터 발생하는 이벤트를 받는 클래스'''
    async def on_connect(self, connection: 'Connection'):
        raise NotImplementedError

    async def on_recv(self, connection: 'Connection', msg: str):
        raise NotImplementedError

    async def on_disconnect(self, connection: 'Connection'):
        raise NotImplementedError

class Connection:
    '''접속이 발생했을때 생성되는 클래스'''
    def __init__(self, writer):
        self._send_queue: asyncio.Queue = asyncio.Queue()
        self._writer = writer
        self._extra_data = None

    async def handle_recv(self, reader: asyncio.StreamReader, recv_event):
        '''peer로 부터 메시지가 도착했을때를 처리하는 coroutine'''
        while True:
            try:
                data = await reader.read(1024)
            except ConnectionResetError:
                break
            except BrokenPipeError:
                break

            #접속이 끊겼을때 처리.
            if not data:
                break

            #negotiation 데이터 필터링(첫번째 값이 IAC이면 3바이트를 날려버림)
            if data[0] == IAC:
                data = data[3:]

            #도착한 메시지가 스트링이 아닌 경우 무시.
            try:
                msg = data.decode()
            except UnicodeError:
                continue
          
            replace_msg = msg.replace('\r\n', '')
            await recv_event(self, replace_msg)

        self.disconnect()
        await self._send_queue.put(None)
        
    async def handle_send(self, writer: asyncio.StreamWriter):
        '''send queue에 보낼데이터가 도착하면 peer에게 보내는 coroutine'''
        while True:
            send_data = await self._send_queue.get()
            if send_data is None:
                break
            writer.write(send_data)
            try:
                await writer.drain()
            except ConnectionResetError:
                break
            except BrokenPipeError:
                break
        
    def disconnect(self):
        self._writer.close()

    def send(self, msg: str):
        self._send_queue.put_nowait(msg.encode())

    def set_extra_data(self, extra_data):
        '''사용하는 측에서 추가적인 정보를 저장하기 위한 method'''
        self._extra_data = extra_data

    def get_extra_data(self):
        '''저장된 추가정보를 리턴하는 method'''
        return self._extra_data

    def set_echo_mode(self, is_enable: bool):
        if is_enable:
            self._send_queue.put_nowait(bytes([0xff, 0xfc, 0x01]))
        else:
            self._send_queue.put_nowait(bytes([0xff, 0xfb, 0x01]))

class ConnectionManager:
    def __init__(self, event: ConnectionManagerEventBase):
        self._server = None
        self._loop = None
        self._event = event

    async def handle_accept(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        '''새로운 접속이 발생했을때를 처리하는 coroutine'''
        connection = Connection(writer)
        recv_future = asyncio.create_task(connection.handle_recv(reader, self._event.on_recv))
        send_future = asyncio.create_task(connection.handle_send(writer))

        await self._event.on_connect(connection)

        await recv_future
        await send_future

        await self._event.on_disconnect(connection)

    def start_server(self, listen_addr: str, port: int, loop):
        coro = asyncio.start_server(self.handle_accept, listen_addr, port, loop=loop)
        self._server = loop.run_until_complete(coro)
        self._loop = loop

    def close(self):
        self._server.close()
        self._loop.run_until_complete(self._server.wait_closed())

    def get_listen_addr(self) -> str:
        return self._server.sockets[0].getsockname()[0]

    def get_listen_port(self) -> int:
        return self._server.sockets[0].getsockname()[1]
    
class ConnectionManagerEventTest(ConnectionManagerEventBase):
    async def on_disconnect(self, connection: Connection):
        print('disconnect')

    async def on_recv(self, connection: Connection, msg: str):
        replace_msg = msg.replace('\r\n', '\n')
        print('recv : ' + replace_msg)

    async def on_connect(self, connection: Connection):
        print('connect')   

if __name__ == '__main__': 
    loop = asyncio.get_event_loop()
    connection_manager = ConnectionManager(ConnectionManagerEventTest())
    connection_manager.start_server('127.0.0.1', 8888, loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    connection_manager.close()
    loop.close()

    
