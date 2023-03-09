from . import batteries
from .utils import clientid

import paho.mqtt.client as mqtt

device = mqtt.Client(clientid)
topic = f'kilats/v1/{clientid}/'
isConnected = False

config = {
    'mqtt_host': "147.139.166.233",
    'mqtt_port': 4118,
    'mqtt_uname': "kilatsdevicex",
    'mqtt_pass': "Mac57588."}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global isConnected
        isConnected = True
        print("mqtt connected")

        def on_message(client, userdata, msg):
            topicnya = msg.topic.replace(topic, '')
            payload = msg.payload.decode("utf-8")

            if "open/" in topicnya:
                r = int(topicnya.replace("open/", ""))
                for i in range(len(batteries.racks)):
                    if int(r) == batteries.find_racks(batteries.racks[i]):
                        for z in range(10):
                            try:
                                batteries.racks[i].write_register(21, 1)
                                print(f"door open in rack {r} with rackid: {batteries.racks[i].address}")
                                break
                            except:
                                continue
                        break

        client.on_message = on_message
        client.subscribe(
            topic=f'{topic}#',
            qos=2)

    else:
        print(f'Failed to connect error code: {rc}')
        isConnected = False

def on_disconnect(client, userdata,  rc):
    global isConnected
    isConnected = False
    print("mqtt disconnected")
