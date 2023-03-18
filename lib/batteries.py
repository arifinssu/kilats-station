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

    addresses.append(instrument(11, baud, port))
    addresses.append(0)
    addresses.append(instrument(12, baud, "/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066DFF545052836687063225-if02"))
    # for i in range(32):
    #     i = instrument(start + i, baud, port)
    #     try: 
    #         i.read_registers(0, 2)
    #         i.serial.timeout = 1
    #         print(i)
    #         addresses.append(i)
    #     except: del i
    #     delay(100)
    print(addresses)
    global racks
    racks = addresses
    return addresses

def find_racks(rack):
    try: return (rack.address - first_rack) + 1
    except: return None


# def dummybat():
#     data = None
#     for z in range(10):
#         try:
#             data = racks[1].read_register(20)
#             # print(rack.address, data)
#             delay(100)
#             break
#         except: continue

#     return dumps({
#         'battery_id': 2726297616,
#         'is_charging': False,
#         'temperature': 23,
#         'capacity': 25600,
#         'percent': 99,
#         'current': 1,
#         'voltage': 47,
#         'cells': [3783, 3778, 3777, 3778, 3781, 3782, 3782, 3779, 3779, 3784, 3785, 3780],
#         'door': ("close" if data == 0 else "open"),
#         'curr_charge': "8.0",
#         'port_connect': "true"
    # })

def get_data(rack):
    data = None
    port_connect = False
    success = False

    for z in range(20):
        try:
            data = rack.read_registers(0, 23)
            # print(rack.address, data)
            delay(100)
            success = True
            port_connect = True
            break
        except: continue

    if not success: 
        data = [0] * 23
        perc = 0
        cap = 0

    # print(data)
    # try: 
    #     data = rack.read_registers(0, 23)
    #     port_connect = True
    # except Exception as e: 
    #     # print(f"device {rack.address} disconnected. {e}")
    #     # delay(1000)
    #     port_connect = False
    #     data = [0] * 23

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