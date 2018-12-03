#async_input.py
import sys
import select
import asyncio

read_list = [sys.stdin]

def read():
    '''
    라인단위로 키보드의 입력을 받아 리턴하는 함수.
    비동기로 실행됨.
    '''
    global read_list
    results = []
    ready = select.select(read_list, [], [], 0.00000001)[0]
    if not ready:
        return results

    for file in ready:
        line = file.readline()
        split_lines = line.split('\n')
        results += [a for a in split_lines if a != '']

    return results

async def async_read():
    loop = asyncio.get_event_loop()
    results = []
    line = await loop.run_in_executor(None, sys.stdin.readline)
    if not line:
        return []
    
    split_lines = line.split('\n')
    results += [a for a in split_lines if a != '']

    return results

async def test():
    while True:
        result = await async_read()
        print(result)
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())