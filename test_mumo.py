__version__     = '0.1.1'
__author__      = 'monstermac-rnd'
__description__ = """
kilats project monstermac, kilats-station section.
- add racks array segmentation
                  """

from api import app
from lib import gateway
from lib.timer import (Timer, millis, delay)
from lib.utils import (mqtt_config, uport, ubaud, rack_slot, clientid, HREG_TOTAL)
from lib.battery import battery
from lib.gateway import gtwy

# import minimalmodbus
import json
import threading
import sys
import logging

from lib.modbus import Modbus
from random import randint

test = [0, 0]
for i in range(2):
    address = Modbus(i+1, ubaud, uport)
    address.set_mode('HREG', HREG_TOTAL)
    address.set_timeout(1)
    try:
        address.start()
        address.set_timeout(1)
        test[i] = address
    except: del address
# test = Modbus(3, ubaud, uport)
# test.set_mode('HREG', HREG_TOTAL)
# test.start()

def main2():
    while True:
        val = randint(0, 1)
        for i in range(2):
            if test[i].set_data('HREG', 14, val):
                print("main2", test[i].get_data('HREG'))
                print()
            delay(75)

def main():
    threading.Thread(
        target=main2,
        args=(), 
        daemon=True
    ).start()

    while True:
        val = randint(0, 999)
        for i in range(2):
            if test[i].set_data('HREG', 13, val):
                print("main", test[i].get_data('HREG'))
                print()
            delay(25)


# def main():
#     gateway.start(
#         mqtt_config['user'],
#         mqtt_config['pass'],
#         mqtt_config['host'],
#         mqtt_config['port'])

#     battery.config(uport, ubaud, 2)
#     battery.init()
#     battery_data_temp = [0] * battery.maks

#     dataloop = Timer()
#     dataloop.delay(1000)

#     while True:
#         battery.update()

#         if dataloop.loop():
#             try:
#                 for rack in range(len(battery.racks)):
#                     if battery.racks_data[rack] != battery_data_temp[rack]:
#                         battery_data_temp[rack] = battery.racks_data[rack]
#                         if gateway.isConnected:
#                             gateway.publish(
#                                 topic = f"{gateway.topic}data/{rack+1}",
#                                 payload = json.dumps(battery_data_temp[rack]))

#                         # print(f"{millis()} - {battery.racks_data[rack]} - {gateway.topic}data/{rack+1}")
#             except Exception as e: 
#                 print(e)
#                 pass

if __name__ == '__main__':
    try:
        threading.Thread(
            target=main,
            args=(), 
            daemon=True
        ).start()
        
        app.run(
            host="0.0.0.0",
            port=4646)

    except RuntimeError as RE:
        sys.exit(f"main runtime error: {RE}")

    except Exception as e:
        sys.exit(f"main exception: {e}")

    except KeyboardInterrupt:
        sys.exit("main exit")