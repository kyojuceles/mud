#timer.py
import time

class Timer:
    '''
    interval만큼 시간이 지나면 is_signal()이 True를 리턴한다.
    is_signal()이 True를 리턴한 이후 초기화 되고 동작을 반복한다.
    interval의 단위는 1초이다.
    '''
    def __init__(self, interval_second: float):
        self._interval_second = interval_second
        self._start_time = time.time()

    def _reset(self):
        self._start_time = time.time()

    def is_signal(self):
        elapse = time.time() - self._start_time
        if elapse >= self._interval_second:
            self._reset()
            return True
        return False

