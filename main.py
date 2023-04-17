__version__     = '0.2.2'
__author__      = 'monstermac-rnd'
__description__ = """
kilats project monstermac, kilats-station section.
- p2
- threaded modbus rack
- cabinet control added
                  """

import sys
from src.config import config
if not config.init('bin/config.ini'):
    sys.exit('config not found')

from api import app
from src import gateway
from src.timer import (Timer, millis, delay)
from src.utils import (mqtt_config)
from src.battery import battery
from src.cabinet import cabinet

import threading
import logging
import json

def main():
    gateway.start(
        mqtt_config['user'],
        mqtt_config['pass'],
        mqtt_config['host'],
        mqtt_config['port'])

    cabinet.config(
        int(config.read()['cabinet']['address']),
        config.read()['cabinet']['port'],
        int(config.read()['cabinet']['baud']))
    cabinet.init()
    cabinet_data_temp = None

    battery.config(
        config.read()['rack']['port'],
        int(config.read()['rack']['baud']),
        int(config.read()['rack']['slot']))
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
                        if gateway.isConnected:
                            battery_data_temp[rack] = battery.racks_data[rack]
                            gateway.publish(
                                topic = f"{gateway.rack_topic}data/{rack+1}",
                                payload = json.dumps(battery_data_temp[rack]))

                        # print(f"{millis()} - {battery.racks_data[rack]} - {gateway.slot_topic}data/{rack+1}")

                if cabinet_data_temp != cabinet.get_data():
                    if gateway.isConnected:
                        cabinet_data_temp = cabinet.get_data()
                        gateway.publish(
                            topic = f"{gateway.cabinet_topic}data",
                            payload = json.dumps(cabinet_data_temp))

            except Exception as e: 
                print(e)
                pass

if __name__ == '__main__':
    try:
        # threading.Thread(
        #     target=main,
        #     args=(), 
        #     daemon=True
        # ).start()
        main()
        
        # app.run(
        #     host="0.0.0.0",
        #     port=4646)

    except RuntimeError as RE:
        sys.exit(f"main runtime error: {RE}")

    except Exception as e:
        sys.exit(f"main exception: {e}")

    except KeyboardInterrupt:
        sys.exit("main exit")