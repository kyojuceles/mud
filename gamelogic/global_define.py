'''
global_define.py

전역으로 사용되는 값들의 모임
'''

ENTER_ROOM_ID = '광장_00_00'
UPDATE_INTERVAL = 1
TICK_FOR_UPDATE_RECOVERY = 30
CONSOLE_PLAYER_ID = -1

welcome_msg = '==============================================================\n'\
              '접속을 환영합니다!\n'\
              '도움말은 [도움말] 또는 [help] 명령어를 사용하면 볼 수 있습니다.\n'\
              '명령어를 사용하실때 []는 치지 말아주세요.\n'\
              '==============================================================\n'

help_msg = '[도움말]\n'\
           '[도움말, help]\t\t\t : 도움말을 본다.\n'\
           '[공격, attack] [대상]\t\t : 대상을 공격한다.\n'\
           '[동, 서, 남, 북, e, w, s, n]\t : 해당 방향으로 이동한다.\n'\
           '[본다, see]\t\t\t : 현재 맵을 본다.\n'\
           '[상태, status]\t\t\t : 플레이어의 상태를 본다.\n'\
           '[도망, flee]\t\t\t : 전투중일때 도망을 간다.\n'\
           '[재시작, respawn]\t\t : 사망상태에서 재시작을 한다.\n'\
           '[말하기, say] [메시지]\t\t : 방안에 있는 플레이어들에게 메시지를 보낸다.\n'\
           '[외치기, shout] [메시지]\t : 접속한 모든 플레이어들에게 메시지를 보낸다.\n'\
           '[소지품, inventory]\t\t : 소지품을 본다.\n'\
           '[나가기, exit]\t\t\t : 접속을 종료한다.\n'

login_name_msg = '이름을 입력해주세요. \'새로만들기\'또는 \'register\'를 입력하시면 캐릭터를 생성합니다.\n'
login_name_not_exist_msg = '계정이 존재하지 않습니다.\n'
login_name_duplicate_msg = '이미 접속중인 이름입니다.\n'
login_password_msg = '패스워드를 입력해주세요.\n'
login_fail_msg = '로그인이 실패했습니다.\n'
create_account_name_msg = '사용할 이름을 입력하세요.(20자이내)\n'
create_account_password_msg = '사용할 패스워드를 입력하세요.(20자이내)\n'
login_password_invalid_msg = '패스워드가 잘못 입력되었습니다. 다시 입력해주세요.\n'
create_account_name_ban_msg = '입력한 이름은 금지단어라 사용할 수 없습니다.\n'
create_account_name_already = '이미 존재하는 계정입니다.\n'
create_account_name_not_space_msg = '이름에는 공백이 포함되어서는 안됩니다.\n'
create_account_fail_msg = '계정을 생성하는데 실패했습니다.\n'

ban_account_list = set(['새로만들기'])
