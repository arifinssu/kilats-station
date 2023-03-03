from . import gateway
from .utils import (millis, uint16_to_int16, delay, from16to32)

import minimalmodbus
from json import dumps

def instrument(address, baud, port, closePort=True):
    device = minimalmodbus.Instrument(port, address)
    device.serial.baudrate = baud
    device.serial.timeout  = 0.05
    device.close_port_after_each_call = closePort
    return device

def shelfes(port, baud):
    addresses = []
    for i in range(200):
        i = instrument(i, baud, port)
        try: 
            i.read_registers(0, 23)
            addresses.append(i)
        except: del i
    
    return addresses

def find_shelfes(shelf):
    try: return shelf.address
    except: return None

def get_data(shelf):
    try: data = shelf.read_registers(0, 23)
    except: data = [0] * 23

    batt_id = from16to32(data[0], data[1])
    batt_current = uint16_to_int16(data[2]) / 10
    batt_voltage = data[3] / 1000
    batt_capacity = data[4]
    batt_percent = data[5]
    batt_charge = (True if data[6] == 255 else False)
    batt_temperature = data[7] / 10
    batt_cells = [cells / 1000 for cells in data[8:20]]
    door_status = ("close" if data[20] == 0 else "open")
    current_charge = data[22] / 10

    result = dumps({ 
        'battery_id': batt_id,
        'is_charging': batt_charge,
        'temperature': batt_temperature,
        'capacity': batt_capacity,
        'percent': batt_percent,
        'current': batt_current,
        'voltage': batt_voltage,
        'cells': batt_cells,
        'door': door_status, 
        'curr_charge': current_charge})

    return result

if __name__ == '__main__':
    x = shelfes("/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_0671FF515349836687012759-if02", 19200)
    print(len(x))
    print(find_shelfes(x[0]))