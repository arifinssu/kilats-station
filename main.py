__version__     = '0.2.1'
__author__      = 'monstermac-rnd'
__description__ = """
kilats project monstermac, kilats-station section.
- p2
                  """

from api import app
from lib import gateway
from lib.timer import (Timer, millis, delay)
from lib.utils import (mqtt_config, uport, ubaud, rack_slot, clientid, HREG_TOTAL)
from lib.battery import battery
from lib.gateway import gtwy

import json
import threading
import sys
import logging

def main():
    gateway.start(
        mqtt_config['user'],
        mqtt_config['pass'],
        mqtt_config['host'],
        mqtt_config['port'])

    battery.config(uport, ubaud, 10)
    battery.init()
    battery_data_temp = [0] * battery.maks

    dataloop = Timer()
    dataloop.delay(1000)

    while True:
        battery.update()

        if dataloop.loop():
            try:
                for rack in range(len(battery.racks)):
                    if battery.racks_data[rack] != battery_data_temp[rack]:
                        battery_data_temp[rack] = battery.racks_data[rack]
                        if gateway.isConnected:
                            gateway.publish(
                                topic = f"{gateway.topic}data/{rack+1}",
                                payload = json.dumps(battery_data_temp[rack]))

                        # print(f"{millis()} - {battery.racks_data[rack]} - {gateway.topic}data/{rack+1}")
            except Exception as e: 
                print(e)
                pass

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