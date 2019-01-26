import paho.mqtt.client as mqtt
#import classifier


MQTT_SERVER = '136.60.227.124'
MQTT_PATH = 'test_img'

def on_connect(client, userdata, flags, rc):
    print("Connect" + str(rc))
    client.subscribe(MQTT_PATH)

def on_message(client, userdata, msg):
    print("Topic : ", msg.topic)
    #print(msg.payload)
    # f = open("mqtt_img/output.jpg", "wb")
    # f.write(msg.payload)
    # f.close()
    # classifier.analyzie(msg.payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

client.loop_forever()
