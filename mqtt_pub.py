import paho.mqtt.publish as publish


MQTT_SERVER = 'localhost'
MQTT_PATH = 'test_img'


f = open('car-left.jpg', 'rb')
file_content = f.read()
img = bytearray(file_content)


publish.single(MQTT_PATH, img, hostname=MQTT_SERVER)
