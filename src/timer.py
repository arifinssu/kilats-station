import time

class Timer():
    def __init__(self):
        self._timestamp = 0
        self._delay = 0

    def timeout(self):
        return ((millis() - self._timestamp) > self._delay)

    def delay(self, delay):
        self._timestamp = millis()
        self._delay = delay

    def loop(self):
        if not ((millis() - self._timestamp) > self._delay): return False
        self._timestamp = millis()
        return True

def millis():
    return round(time.time() * 1000)

def delay(delay):
    t0 = millis()
    while (millis() - t0) < delay:
        pass
