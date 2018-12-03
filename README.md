# mud
mud project with python 3.7.0

# 최신버전 빌드
https://github.com/kyojuceles/mud/raw/master/release/win32/mud_2018_12_03.zip

# 시작하기
1. mysql을 설치한다. https://www.mysql.com/
2. mysql에 schema.sql를 import 시킨다.
3. config.ini.example을 config.ini로 이름을 바꾼다.
4. main.exe를 실행한다.

# config.ini 설정하기
[SERVER]<br>
LISTEN_PORT : 접속을 받을 포트번호.<br>
<br>
[DATABASE]<br>
HOST : mysql server의 주소.<br>
USER : mysql에 접속할 때 사용할 user account.<br>
PASSWORD : mysql에 접속할 때 사용할 user password.<br>
DB_NAME : 데이터베이스 이름.<br>
<br>
# console command
main.exe를 실행시킨 이후에 '접속'을 입력하면 로컬에서 접속이 가능하다.
