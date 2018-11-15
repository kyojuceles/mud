#sequence_number_generator.py

class SeqNumGenerator:
    '''
    순차적으로 증가하는 숫자를 생성하는 생성기
    max_num을 넘어서면 start_num으로 회귀한다.
    '''
    def __init__(self, max_num: int, start_num: int = 0):
        self._start_num = start_num
        self._max_num = max_num
        self._next_num = start_num

    def generate(self) -> int:
        num = self._next_num
        self._next_num += 1
        if self._next_num > self._max_num:
            self._next_num = self._start_num
            
        return num
        
        

    