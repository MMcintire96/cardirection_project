import paho.mqtt.publish as publish
import json
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2
import subprocess


MQTT_SERVER = '<<ADD YOUR IP>>'
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
>>>>>>> a5ae7a5cd87ac88592f669055db2ca6ca552f9ac

# this fails if camera is moved from original capture point, or if lighting changes
def captureFirst():
    print("Taking the first frame photo for motion analysis")
    camera.capture('firstimg.jpg')
    stillImg = cv2.imread('firstimg.jpg')
    grayStill = cv2.cvtColor(stillImg, cv2.COLOR_BGR2GRAY)
    return grayStill


def mse(grayStill, grayFrame):
    # mse = summation of i,j vectors subtracted and squared / mn
    # must divide to get err
    mse = np.sum((grayStill.astype("float") - grayFrame.astype("float")) ** 2)
    mse /= float(grayStill.shape[0] * grayStill.shape[1])
    return mse


#TODO send the lot_id, the mse and err here?
def pub_message(image):
    camera.capture('photos/test.jpg')
    f = open('photos/test.jpg', 'rb')
    file_content = f.read()
    publish.single('test_img', payload=file_content, hostname=MQTT_SERVER)
    publish.single('test_lot', payload='12', hostname=MQTT_SERVER)


#load camera - let sleep to init 
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(320, 240))
time.sleep(5)
grayStill = captureFirst()


mseArr = []
def init_mse_arr(grayFrame):
    x = mse(grayStill, grayFrame)
    mseArr.append(x)

def frame_arr(image):
    MSE = mse(grayStill, grayFrame)
    mseArr.append(MSE)
    err = mseArr[9] - mseArr[0]
    if len(mseArr) >= 9:
        mseArr.pop(0)
    return err

i = 0
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # cleans each frame 
    rawCapture.truncate()
    rawCapture.seek(0)

    # get ready for motion analysis
    image = frame.array
    grayFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if i < 10:
        init_mse_arr(grayFrame)
        i += 1
        print("Preparing the video stream with %s frames" %i)
    else:
        # get dx/dt of motion and post
        err = frame_arr(grayFrame)
        publish.single('test_err', payload=err, hostname=MQTT_SERVER)

        # get MSE to post and action
        MSE = mse(grayStill, grayFrame)
        publish.single('test_mse', payload=MSE, hostname=MQTT_SERVER)

        if abs(err) > 100:
            print('Motion detected - publishing to mqtt')
            pub_message(image)
