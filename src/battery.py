from .config import config
from .utils import (uint16_to_int16, from16to32)
from .timer import delay, millis

import minimalmodbus
from threading import Thread

def instrument(address, baud, port, timeout = .1, close_port=True):
    device = minimalmodbus.Instrument(port, address)
    device.serial.baudrate = baud
    device.serial.timeout  = timeout
    device.close_port_after_each_call = close_port
    return device

class BATTERY():
    def __init__(self):
        self.port = None
        self.baud = None
        self.racks = None
        self.maks = 32
        self.racks_data = []
        self.swap = False
        self.swap_from = None
        self.swap_to = None
        self.open_racknum = None
        self.trigger_limit = None
        self.trigger_block = None

    def config(self, port, baud, maks):
        self.port = port
        self.baud = baud
        self.maks = maks

    def init(self):
        self.racks = [0] * self.maks
    
        for i in range(self.maks):
            address = instrument(i+1, self.baud, self.port)
            try: 
                address.read_registers(0, int(config.read()['rack']['HREG_TOTAL']))
                address.serial.timeout = 1
                self.racks[i] = address
            except: del address
            delay(50)

        self.racks_data = [0] * len(self.racks)

    def get_data(self, rack):
        try: 
            batt_data = rack.read_registers(0, int(config.read()['rack']['HREG_TOTAL']))
            port_connect = "connected"
        except Exception as e:
            port_connect = "disconnected"
            batt_data = [0] * int(config.read()['rack']['HREG_TOTAL'])

        batt_id = from16to32(batt_data[0], batt_data[1])
        batt_current = uint16_to_int16(batt_data[2]) / 10
        batt_voltage = "{:.1f}".format(batt_data[3] / 1000)
        batt_capacity = batt_data[4]
        batt_percent = batt_data[5]
        batt_temperature = batt_data[6] / 10
        status = ("charging" if batt_data[7] == 255 else "idle")
        ntc_temp = round(batt_data[8] / 10)
        power_supply_voltage = "{:.1f}".format(batt_data[9] / 1000)
        battery_supply_voltage = "{:.1f}".format(batt_data[10] / 1000)
        supply_current = 0 if batt_data[11] < 500 else "{:.1f}".format(batt_data[11] / 1000)

        door_status = ("close" if batt_data[12] == 0 else "open")
        current_limit = batt_data[14] / 10
        block_charge = (True if batt_data[15] == 1 else False)

        return {
            'battery': {
                'port': port_connect,
                'id': batt_id,
                'capacity': batt_capacity,
                'percent': batt_percent,
                'voltage': batt_voltage,
                'current': batt_current,
                'temperature': batt_temperature,
                'door': door_status,
            },
            'charger': {
                'status': status,
                'disable': block_charge,
                'voltage': battery_supply_voltage,
                'supply_voltage': power_supply_voltage,
                'current': supply_current,
                'limit_current': current_limit,
                'ntc_temperature': ntc_temp,
            }
        }

    def open_rack(self, racknum):
        self.racks[racknum].write_register(13, 1)
        # try:
        #     self.racks[racknum].write_register(12, 1)
        #     delay(500)
        #     return True if self.racks[racknum].read_register(11) == 1 else False
        # except: return False

    def open_rack_async(self, num):
        self.open_racknum = num

    def transfer(self, racknum):
        self.open_rack_async(racknum)
        delay(2000)
        while self.racks_data[racknum]['battery']['door'] == "open": continue
        delay(5000)
        if self.racks_data[racknum]['battery']['id'] == 0: return False
        return True

    def swap_process(self):
        while not self.transfer(self.swap_from): continue
        while self.transfer(self.swap_to): continue
        # swap done
        self.swap = False

        print(f"swapping process from {self.swap_from+1} to {self.swap_to+1} completed")

    def swapping(self, f, t):
        if self.is_swap(): return
        self.swap_from = f
        self.swap_to = t
        self.swap = True
        if self.swap:
            Thread(target=self.swap_process, args=(), daemon=True).start()

    def set_swap(self, value):
        self.swap = value

    def is_swap(self):
        return self.swap

    def set_block_rack(self, data):
        self.trigger_block = data

    def set_limitcc_rack(self, data):
        self.trigger_limit = data

    def update(self):
        if self.open_racknum is not None:
            self.open_rack(self.open_racknum)
            self.open_racknum = None
            delay(50)

        if self.trigger_limit is not None:
            data = self.trigger_limit.split("/")
            racknum = int(data[0])
            value = int(data[1])
            self.racks[racknum].write_register(14, value)
            self.trigger_limit = None
            delay(50)

        if self.trigger_block is not None:
            data = self.trigger_block.split("/")
            racknum = int(data[0])
            value = int(data[1])
            self.racks[racknum].write_register(15, value)
            self.trigger_block = None
            delay(50)

        for racknum in range(len(self.racks)):
            self.racks_data[racknum] = self.get_data(self.racks[racknum])
            delay(50)

battery = BATTERY()