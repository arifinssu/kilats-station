__version__     = '0.1.0'
__author__      = 'monstermac-rnd'
__description__ = """
kilats project monstermac, kilats-station section.
                  """

from api import app
from lib import gateway
from lib import batteries
from lib.utils import (millis, delay, mqtt_config)

import minimalmodbus
import json
import threading
import sys
import logging

def main():
    # import minimalmodbus
    # from time import sleep

    # instrument = minimalmodbus.Instrument("/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0", 12)
    # instrument.serial.baudrate = 19200
    # instrument.serial.timeout  = 1

    # sleep(2)

    # while True:
    #     data = None
    #     success = False
    #     for z in range(10):
    #         try:
    #             data = instrument.read_registers(0, 23)
    #             # delay(100)
    #             # data = instrument.read_register(5)
    #             # delay(100)
    #             # data = instrument.read_register(20)
    #             delay(100)
    #             success = True
    #             break
    #         except: continue

    #     if not success: 
    #         data = [0] * 23

    #     print(data, success)
    #     delay(1000)

    gateway.device.on_connect = gateway.on_connect
    gateway.device.on_disconnect = gateway.on_disconnect
    gateway.device.username_pw_set(mqtt_config['user'], mqtt_config['pass'])
    gateway.device.connect(mqtt_config['host'], mqtt_config['port'])
    gateway.device.loop_start()

    rack = batteries.start_racks(11, "/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0", 19200)

    next_loop = millis()
    next_loop2 = millis()

    while True:
        if millis() >= next_loop + 1000:
            next_loop = millis()
            
            data = []
            for i in rack:
                data.append(batteries.get_data(i))
                delay(100)

            try:
                if gateway.isConnected:
                    gateway.device.publish(
                        topic=f"{gateway.topic}data/{batteries.find_racks(rack[0])}", 
                        payload=data[0],
                        qos=2, 
                        retain=False)

                    gateway.device.publish(
                        topic=f"{gateway.topic}data/2", 
                        payload=data[1],
                        qos=2, 
                        retain=False)

                    gateway.device.publish(
                        topic=f"{gateway.topic}data/3", 
                        payload=data[2],
                        qos=2, 
                        retain=False)
                print(f"{millis()} - {data[0]}")
                print(f"{millis()} - {data[2]}")
                print()
            except: pass

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