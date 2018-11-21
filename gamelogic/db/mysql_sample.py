#mysql_sample.py
from asyncio import events
import tormysql

pool = tormysql.ConnectionPool(
   max_connections = 20, #max open connections
   idle_seconds = 7200, #conntion idle timeout time, 0 is not timeout
   wait_connection_timeout = 3, #wait connection timeout
   host = "127.0.0.1",
   user = "root",
   passwd = "ghddlcjswo",
   db = "mud_db",
   charset = "utf8"
)

async def test():
   async with await pool.Connection() as conn:
       try:
           async with conn.cursor() as cursor:
               await cursor.execute("INSERT INTO player (password, name, lv, xp) values ('pa12345', 'kyojuceles3, 1, 0) ")
       except Exception as inst:
           await conn.rollback()
           print(inst)
       else:
           await conn.commit()

       async with conn.cursor() as cursor:
           await cursor.execute("SELECT * FROM player")
           datas = cursor.fetchall()

   print(datas)

   await pool.close()

ioloop = events.get_event_loop()
ioloop.run_until_complete(test())