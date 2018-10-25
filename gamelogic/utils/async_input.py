#async_input.py

import sys
import select

read_list = [sys.stdin]

def read():
    global read_list
    results = []
    ready = select.select(read_list, [], [], 0.00000001)[0]
    if not ready:
        return results

    for file in ready:
        line = file.readline()
        result = line.split('\n')
        results += [a for a in result if a != '']

    return results