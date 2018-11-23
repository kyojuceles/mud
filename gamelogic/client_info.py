
#client_info.py

from .components.gameobject import GameObject

class ClientInfo:
    '''
    클라이언트의 정보를 가지고 있는 클래스
    '''
    STATUS_NOT_CONNECT: int = 0
    STATUS_LOGIN_NAME: int = 1
    STATUS_LOGIN_PASSWORD: int = 2
    STATUS_CREATE_ACCOUNT_NAME: int = 3
    STATUS_CREATE_ACCOUNT_PASSWORD: int = 4
    STATUS_LOGIN: int = 5

    def __init__(self, send_func = None, disconnect_func = None, set_echo_mode_func = None):
        self._tag = None
        self._status = ClientInfo.STATUS_NOT_CONNECT
        self._send_func = send_func
        self._disconnect_func = disconnect_func
        self._set_echo_mode_func = set_echo_mode_func
        self._name = ''
        self._player = None

    def deinitialize(self):
        self._tag = None
        self._send_func = None
        self._disconnect_func = None
        self._set_echo_mode_func = None

    def set_status(self, status: int):
        self._status = status
    
    def get_status(self) -> int:
        return self._status

    def send(self, msg: str):
        if self._send_func:
            replace_msg = msg.replace('\n', '\r\n')
            self._send_func(replace_msg)
            return

        print(msg, end = '')
    
    def disconnect(self):
        if self._disconnect_func:
            self._disconnect_func()
        
    def set_echo_mode(self, is_enable):
        if self._set_echo_mode_func:
            self._set_echo_mode_func(is_enable)

    def set_player(self, player: GameObject):
        self._player = player

    def get_player(self) -> GameObject:
        return self._player

    def set_player_name(self, name: str):
        self._name = name

    def get_player_name(self):
        return self._name