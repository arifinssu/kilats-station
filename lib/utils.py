from ctypes import c_long

uport = "/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0"
ubaud = 19200
rack_slot = 10

clientid = "KILATSDEVX-C1000"
HREG_TOTAL = 16

mqtt_config = {
    'host': "147.139.166.233",
    'port': 4118,
    'user': "kilatsdevicex",
    'pass': "Mac57588."}

def uint16_to_int16(raw):
    if raw > 32767: return (65535 - raw)
    return raw

def from16to32(data16a, data16b):
    if data16a == 0 and data16b == 0: return 0
    result = c_long((data16a << 16) | (data16b)).value
    if result < 2147483647: return (result + 2147483647)
    return result