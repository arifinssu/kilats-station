from .config import config
from .utils import (uint16_to_int16, from16to32)
from .timer import delay, millis

import minimalmodbus

def instrument(address, baud, port, timeout = 1, close_port=True):
    device = minimalmodbus.Instrument(port, address)
    device.serial.baudrate = baud
    device.serial.timeout  = timeout
    device.close_port_after_each_call = close_port
    return device

class CABINET():
    def __init__(self):
        self.address = None
        self.port = None
        self.baud = None
        self.cabinet = None

    def config(self, address, port, baud):
        self.address = address
        self.port = port
        self.baud = baud

    def init(self):
        # try:
        #     self.cabinet = instrument(self.address, self.baud, self.port)
        #     delay(2000)
        #     self.cabinet.read.registers(0, int(config.read()['cabinet']['HREG_TOTAL']))
        #     return True
        # except:
        #     self.cabinet = None
        #     return False
        self.cabinet = instrument(self.address, self.baud, self.port)

    def get_data(self):
        try: 
            cabinet_data = self.cabinet.read_registers(0, int(config.read()['cabinet']['HREG_TOTAL']))
            port_connect = "connected"
        except Exception as e:
            port_connect = "disconnected"
            cabinet_data = [0] * int(config.read()['cabinet']['HREG_TOTAL'])

        relay1 = cabinet_data[0]
        relay2 = cabinet_data[1]
        digipot = cabinet_data[2]
        vout1 = cabinet_data[3]
        vout2 = cabinet_data[4]

        remote_ps1 = cabinet_data[5]
        remote_ps2 = cabinet_data[6]
        remote_ps3 = cabinet_data[7]
        remote_ps4 = cabinet_data[8]
        alarm_ps1 = cabinet_data[9]
        alarm_ps2 = cabinet_data[10]
        alarm_ps3 = cabinet_data[11]
        alarm_ps4 = cabinet_data[12]

        voltage = cabinet_data[13]
        ntc_temp1 = round(cabinet_data[14] / 10)
        ntc_temp2 = round(cabinet_data[15] / 10)
        water_sense = cabinet_data[16]
        fire_sense = cabinet_data[17]

        return {
            'cabinet': {
                'port': port_connect,
                'charge_voltage': digipot, #raw
                'fan1': vout1,
                'fan2': vout2,
                'alarm_ps1': alarm_ps1,
                'alarm_ps2': alarm_ps2,
                'alarm_ps3': alarm_ps3,
                'alarm_ps4': alarm_ps4,
                'source_voltage': voltage,
                'temperature1': ntc_temp1,
                'temperature2': ntc_temp2,
                'water_sense': water_sense,
                'fire_sense': fire_sense,
            }
        }

    def control_relay(self, relay, value):
        if value > 1: return

        if relay == 1:
            self.cabinet.write_register(0, value)
        elif relay == 2:
            self.cabinet.write_register(1, value)

        delay(50)
    
    def set_potensio(self, value):
        if value < 0 or value > 255: return
        self.cabinet.write_register(2, value)
        delay(50)

    def control_vout(self, vout, value):
        if value > 1: return

        if vout == 1:
            self.cabinet.write_register(3, value)
        elif vout == 2:
            self.cabinet.write_register(4, value)

        delay(50)

    def control_psu(self, psu, value):
        if value > 1: return

        if psu == 1:
            self.cabinet.write_register(5, value)
        elif psu == 2:
            self.cabinet.write_register(6, value)
        elif psu == 3:
            self.cabinet.write_register(7, value)
        elif psu == 4:
            self.cabinet.write_register(8, value)
        
        delay(50)

cabinet = CABINET()