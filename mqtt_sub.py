import paho.mqtt.client as mqtt

MQTT_SERVER = '136.60.227.124'
MQTT_PATH = 'test_err'


def on_connect(client, userdata, flags, rc):
    print("Connect" + str(rc))
    client.subscribe(MQTT_PATH)
    client.subscribe('test_mse')


def on_message(client, userdata, msg):
    print("Topic : ", msg.topic)
    if msg.topic == 'test_err':
        err = str(msg.payload)
        err = err.replace("b'", "").replace("'", "")
        f = open('testerr.txt', 'a')
        print(err, file=f)
    elif msg.topic == 'test_mse':
        err = str(msg.payload)
        err = err.replace("b'", "").replace("'", "")
        f = open('testmse.txt', 'a')
        print(err, file=f)




client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

client.loop_forever()
