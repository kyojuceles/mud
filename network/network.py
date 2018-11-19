#network.py
import sys
import asyncio

class Connection:
    def __init__(self, writer):
        self._send_queue: asyncio.Queue = asyncio.Queue()
        self._writer = writer

    async def handle_recv(self, reader: asyncio.StreamReader):
        while True:
            data = await reader.readline()
            if not data:
                break
            await self._send_queue.put(data)

    async def handle_send(self, writer: asyncio.StreamWriter):
        while True:
            send_data = await self._send_queue.get()
            writer.write(send_data)
            await writer.drain()
            writer.close()
            break

    def disconnect(self):
        self._writer.close()

    def send(self, msg: str):
        self._send_queue.put_nowait(msg.encode())

class ConnectionManager:
    def __init__(self):
        self._server = None
        self._loop = None

    async def handle_accept(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        connection = Connection(writer)
        recv_future = asyncio.create_task(connection.handle_recv(reader))
        send_future = asyncio.create_task(connection.handle_send(writer))

        await recv_future
        await send_future

        self._on_disconnect(connection)

    def start_server(self, listen_addr: str, port: int) -> asyncio.AbstractEventLoop:
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle_accept, listen_addr, port, loop=loop)
        self._server = loop.run_until_complete(coro)
        self._loop = loop

        # Serve requests until Ctrl+C is pressed
        print('Serving on {}'.format(self._server.sockets[0].getsockname()))

        return loop

    def close(self):
        self._server.close()
    
    def wait_server_closed(self):
        self._loop.run_until_complete(self._server.wait_closed())

    def _on_disconnect(self, connection):
        print('disconnect!!')

if __name__ == "__main__":
    connection_manager = ConnectionManager()
    loop = connection_manager.start_server('127.0.0.1', 8888)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    connection_manager.close()
    connection_manager.wait_server_closed()
    loop.close()

    
