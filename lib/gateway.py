from . import battery
from .utils import clientid
from lib.battery import battery

import paho.mqtt.client as paho

device = paho.Client(clientid)
topic = f'kilats/v1/{clientid}/'
isConnected = False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global isConnected
        isConnected = True
        print("mqtt connected")

        def on_message(client, userdata, msg):
            topicnya = msg.topic.replace(topic, '')
            payload = msg.payload.decode("utf-8")

            if "open/" in topicnya:
                if not battery.is_swap():
                    racknum = int(topicnya.replace("open/", "")) - 1
                    battery.open_rack_async(racknum)
                    client.publish(
                        topic=f'{topic}/open/{racknum+1}',
                        payload='ok',
                        qos=2)
                else:
                    print("this station is in swapping process")
                    client.publish(
                        topic=f'{topic}/open/{racknum+1}',
                        payload='fail',
                        qos=2)

            if "swap/" in topicnya:
                if not battery.is_swap():
                    swap = topicnya.replace("swap/", "").split("/")
                    swap_from = int(swap[0]) - 1
                    swap_to = int(swap[1]) - 1
                    print("battery swapping process", swap_from, swap_to)
                    battery.swapping(swap_from, swap_to)
                else:
                    print("this station is in swapping process")

            if "disable_charge/" in topicnya:
                block = 0
                if payload == "yes": block = 1
                racknum = int(topicnya.replace("disable_charge/", "")) - 1
                battery.set_block_rack(f'{racknum}/{block}')

            if "limit_current/" in topicnya:
                racknum = int(topicnya.replace("limit_current/", "")) - 1
                battery.set_limitcc_rack(f'{racknum}/{payload}')

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

###########

class GATEWAY():
    def __init__(self):
        self.connected = False
        self.client = None
        self.topic = None
        self.mqtt = None
        self.rc = None

    def config(self, us, pw, host, port, idstation, qos, retain=False):
        self.client = f"KILATS-{idstation}"
        self.topic = f'kilats/v1/{self.client}/'
        self.mqtt = paho.Client(self.topic)
        self.mqtt.username_pw_set(us, pw)
        self.host = host
        self.port = port
        self.qos = qos
        self.retain = retain

    def publish(self, topic, payload):
        return self.mqtt.publish(
            topic = topic,
            payload = payload,
            qos = self.qos,
            retain = self.retain)

    def subscribe(self, topic, qos):
        return self.mqtt.subscribe(
            topic = topic,
            qos = qos)

    def on_connect(self, client, userdata, flags, rc):
        self.rc = rc
        print(self.rc)
        if self.rc == 0:
            self.connected = True
            def on_message(self, client, userdata, msg):
                topicnya = msg.topic.replace(topic, '')
                payload = msg.payload.decode("utf-8")

                if "open/" in topicnya:
                    racknum = int(topicnya.replace("open/", ""))
                    for num in range(len(battery.racks)):
                        if racknum == battery.rack[num].address:
                            for open_retries in range(10):
                                try:
                                    battery.rack[num].write_register(21, 1)
                                    print(f"door open in rack {open_retries} with rackid: {battery.rack[num].address}")
                                    break
                                except: continue
                            break

            client.on_message = on_message
            client.subscribe(
                topic=f'{self.topic}#',
                qos=self.qos)

        else:
            self.connected = False

    def is_connected(self):
        return self.connected

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.rc = rc

    def start(self):
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_disconnect = self.on_disconnect
        self.mqtt.connect(self.host, self.port)
        self.mqtt.loop_start()

gtwy = GATEWAY()
