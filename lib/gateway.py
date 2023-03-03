import paho.mqtt.client as mqtt

id_rack = 1
clientid = "KILATSDEVX-C0001"
device = mqtt.Client(clientid)

topic = f'kilats/v1/{clientid}/'
isConnected = False
isOpen = False

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

            if f'open/{id_rack}' in topicnya:
                global isOpen
                openkan = topicnya.replace(f'open/{id_rack}', '')
                print("getopen")
                isOpen = True

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
