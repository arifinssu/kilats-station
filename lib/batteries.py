from . import gateway
from .utils import (millis, uint16_to_int16, delay, from16to32, HREG_TOTAL)

import minimalmodbus
from json import dumps

first_rack = 0
racks = []

def instrument(address, baud, port, closePort=True):
    device = minimalmodbus.Instrument(port, address)
    device.serial.baudrate = baud
    device.serial.timeout  = .1
    device.close_port_after_each_call = closePort
    return device

def start_racks(start, port, baud):
    global first_rack
    first_rack = start

    addresses = []
    for i in range(32):
        i = instrument(start + i, baud, port)
        try: 
            i.read_registers(0, 23)
            i.serial.timeout = 1
            print(i)
            addresses.append(i)
        except: del i
        delay(50)

    global racks
    racks = addresses
    return addresses

def find_racks(rack):
    try: return (rack.address - first_rack) + 1
    except: return None

def get_data(rack):
    try: 
        data = rack.read_registers(0, 23)
        port_connect = True
    except Exception as e: 
        # print(f"device {rack.address} disconnected. {e}")
        # delay(1000)
        port_connect = False
        data = [0] * 23

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
        'curr_charge': current_charge,
        'port_connect': port_connect})

    return result