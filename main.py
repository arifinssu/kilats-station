__version__     = '0.1.0'
__author__      = 'monstermac-rnd'
__description__ = """
kilats project monstermac, kilats-station section.
                  """

from api import app
from lib import gateway
from lib import batteries
from lib.utils import (millis, uint16_to_int16, delay, from16to32)

import minimalmodbus
import json
import threading
import sys

def main():
    gateway.device.on_connect = gateway.on_connect
    gateway.device.on_disconnect = gateway.on_disconnect
    gateway.device.username_pw_set(gateway.config['mqtt_uname'], gateway.config['mqtt_pass'])
    gateway.device.connect(gateway.config['mqtt_host'], gateway.config['mqtt_port'])
    gateway.device.loop_start()

    shelf = batteries.shelfes("/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_0671FF515349836687012759-if02", 19200)

    next_loop = millis()

    while True:
        data = batteries.get_data(shelf[0])

        if millis() >= next_loop + 5000:
            next_loop = millis()
            if gateway.isConnected:
                gateway.device.publish(
                    topic=f"{gateway.topic}data/{gateway.id_rack}", 
                    payload=data,
                    qos=2, 
                    retain=False)
            print(f"{millis()} - {data}")

        if gateway.isOpen:
            print("door open send command")
            device.write_register(21, 1)
            gateway.isOpen = False

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