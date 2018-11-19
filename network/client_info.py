#client_info.py
class ClientInfo:
    '''
    클라이언트의 정보를 가지고 있는 클래스
    '''
    STATUS_NOT_CONNECT: int = 0
    STATUS_NOT_LOGIN: int = 1
    STATUS_LOGIN: int = 2

    def __init__(self, is_console: bool):
        self._is_console = is_console
        self._tag = None
        self._status = ClientInfo.STATUS_NOT_CONNECT

    def set_status(self, status: int):
        self._status = status
    
    def get_status(self) -> int:
        return self._status

    def is_console(self):
        return self._is_console

    def set_tag(self, tag):
        self._tag = tag

    def get_tag(self):
        return self._tag

    def on_receive(self, msg: str):
        print(msg, end = '')