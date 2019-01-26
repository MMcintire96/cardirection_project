import paho.mqtt.publish as publish
import json
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2
import subprocess


MQTT_SERVER = '136.60.227.124'
MQTT_PATH = 'test_img'

# make json serilizable and passable through mqtt - make a byte array passable
def to_json(python_object):
    if isinstance(python_object, time.struct_time):
        return {'__class__': 'time.asctime',
                '__value__': time.asctime(python_object)}
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': list(python_object)}
        raise TypeError(repr(python_object) + ' is not JSON Serializable')

# this fails if camera is moved from original capture point, or if lighting changes
def captureFirst():
    print("Taking the first frame photo for motion analysis")
    subprocess.call("raspistill -w 320 -h 240 -o firstimg.jpg", shell=True)
    stillImg = cv2.imread('firstimg.jpg')
    grayStill = cv2.cvtColor(stillImg, cv2.COLOR_BGR2GRAY)
    return grayStill


grayStill = captureFirst()


def mse(grayStill, grayFrame):
    # mse = summation of i,j vectors subtracted and squared / mn
    # must divide to get err
    err = np.sum((grayStill.astype("float") - grayFrame.astype("float")) ** 2)
    err /= float(grayStill.shape[0] * grayStill.shape[1])

    return err


# find a way to send this just an array -> byte array  == skip writting to rpi
def pub_message():
    camera.capture('photos/test.jpg')
    f = open('test.jpg', 'rb')
    file_content = f.read()
    img = bytearray(file_content)
    msg_obj = {
        'lot_id': '12',
        'img': file_content,
        'enter_dir': 'left'
    }
    publish.single(MQTT_PATH, payload=json.dumps(msg_obj, default=to_json), hostname=MQTT_SERVER)


#load camera - let sleep to init 
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(320, 240))
time.sleep(2)


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # cleans each frame 
    rawCapture.truncate()
    rawCapture.seek(0)
    # get ready for motion analysis
    image = frame.array
    grayFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # get motion analysis and action
    error = mse(grayStill, grayFrame)
    if error > 1000:
        print('Motion detected - publishing to mqtt')
        pub_message()
    else:
        print('NO CHANGE IN MOTION')
