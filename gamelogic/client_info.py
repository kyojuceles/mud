#client_info.py
from .components.gameobject import GameObject

class ClientInfo:
    '''
    클라이언트의 정보를 가지고 있는 클래스
    '''
    STATUS_NOT_CONNECT: int = 0
    STATUS_NOT_LOGIN: int = 1
    STATUS_LOGIN: int = 2

    def __init__(self, is_console: bool):
        self._is_console = is_console
        self._player = None
        self._status = ClientInfo.STATUS_NOT_CONNECT

    def set_status(self, status: int):
        self._status = status
    
    def get_status(self) -> int:
        return self._status

    def is_console(self):
        return self._is_console

    def set_player(self, player: GameObject):
        self._player = player

    def get_player(self) -> GameObject:
        return self._player