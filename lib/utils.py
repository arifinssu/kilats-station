import time
from ctypes import c_long

clientid = "KILATSDEVX-C0032"
HREG_TOTAL = 23

mqtt_config = {
    'host': "147.139.166.233",
    'port': 4118,
    'user': "kilatsdevicex",
    'pass': "Mac57588."}

class Timer():
    def __init__(self):
        self._timestamp = 0
        self._delay = 0

    def timeout(self):
        return ((millis() - self._timestamp) > self._delay)

    def delay(self, delay):
        self._timestamp = millis()
        self._delay = delay

def millis():
    return round(time.time() * 1000)

def delay(delay):
    t0 = millis()
    while (millis() - t0) < delay:
        pass

def uint16_to_int16(raw):
    if raw > 32767: return (65536 - raw)
    return raw

def from16to32(data16a, data16b):
    return c_long((data16a << 16) | (data16b)).value