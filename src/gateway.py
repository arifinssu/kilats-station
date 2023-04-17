from .config import config
from .battery import battery
from .cabinet import cabinet

import paho.mqtt.client as paho

clientid = config.read()['env:kilats']['id']
device = paho.Client(clientid)

topic = f'kilats/v1/{clientid}/'
rack_topic = f'{topic}rack/'
cabinet_topic = f'{topic}cabinet/'
isConnected = False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global isConnected
        isConnected = True
        print("mqtt connected")

        def on_message(client, userdata, msg):
            payload = msg.payload.decode("utf-8")

            if rack_topic in msg.topic:
                command = msg.topic.replace(rack_topic, '')

                if "open/" in command:
                    if not battery.is_swap():
                        racknum = int(command.replace("open/", "")) - 1
                        battery.open_rack_async(racknum)
                        # client.publish(
                        #     topic=f'{rack_topic}open/{racknum+1}',
                        #     payload='ok',
                        #     qos=2)
                    else: print("this station is in swapping process")

                if "swap/" in command:
                    if not battery.is_swap():
                        swap = command.replace("swap/", "").split("/")
                        swap_from = int(swap[0]) - 1
                        swap_to = int(swap[1]) - 1
                        print("battery swapping process", swap_from, swap_to)
                        battery.swapping(swap_from, swap_to)
                    else: print("this station is in swapping process")

                if "disable_charge/" in command:
                    block = 0
                    if payload == "yes": block = 1
                    racknum = int(command.replace("disable_charge/", "")) - 1
                    battery.set_block_rack(f'{racknum}/{block}')

                if "limit_current/" in command:
                    racknum = int(command.replace("limit_current/", "")) - 1
                    battery.set_limitcc_rack(f'{racknum}/{payload}')

            if cabinet_topic in msg.topic:
                command = msg.topic.replace(cabinet_topic, '')

                if "release" in command:
                    cabinet.control_relay(1, int(payload))

                if "charge_voltage" in command:
                    cabinet.set_potensio(int(payload)) #raw

                # if "fan/" in command:
                #     voutnum = int(command.replace("fan/", ""))
                #     cabinet.control_vout(voutnum, int(payload))

                # if "psu/" in command:
                #     psunum = int(command.replace("psu/", ""))
                #     cabinet.control_psu(psunum, int(payload))


        client.on_message = on_message
        client.subscribe(
            topic = f'{topic}#',
            qos   = 2)

    else:
        print(f'Failed to connect error code: {rc}')
        isConnected = False

def on_disconnect(client, userdata,  rc):
    global isConnected
    isConnected = False
    print("mqtt disconnected")

def publish(topic, payload, qos=2, retain=False):
    return device.publish(
        topic = topic,
        payload = payload,
        qos = qos,
        retain = retain)

def start(u, p, host, port):
    device.on_connect = on_connect
    device.on_disconnect = on_disconnect
    device.username_pw_set(u, p)
    device.connect(host, port)
    device.loop_start()