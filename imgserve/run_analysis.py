import subprocess
import time

import cv2
import numpy as np
import paho.mqtt.publish as publish
from picamera import PiCamera
from picamera.array import PiRGBArray

MQTT_SERVER = '136.60.227.124'
motion_filter = .005

#starts the mosquitto dameon in the background
subprocess.call(["mosquitto",  "-d"])


def captureFirst():
    print("Taking the first frame photo for motion analysis")
    camera.capture('firstimg.jpg')
    stillImg = cv2.imread('firstimg.jpg')
    grayStill = cv2.cvtColor(stillImg, cv2.COLOR_BGR2GRAY)
    return grayStill


#load camera - let sleep to init 
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(320, 240))
time.sleep(5)
grayStill = captureFirst()
i = 0
mseArr = []


def mse(grayStill, grayFrame):
    mse = np.sum((grayStill.astype("float") - grayFrame.astype("float")) ** 2)
    mse /= float(grayStill.shape[0] * grayStill.shape[1])
    return mse


def init_mse_arr(grayFrame):
    x = mse(grayStill, grayFrame)
    mseArr.append(x)


def frame_arr(image):
    MSE = mse(grayStill, grayFrame)
    mseArr.append(MSE)
    err = mseArr[len(mseArr)-1] - mseArr[0]
    if len(mseArr) >= i:
        mseArr.pop(0)
    return err


def pub_message(image, err, MSE):
    camera.capture('photos/test.jpg')
    f = open('photos/test.jpg', 'rb')
    file_content = f.read()
    lot_id = 12
    pub_message =  str(lot_id) + ',' + str(err) + ',' + str(MSE)
    publish.single('full_send', payload=pub_message, hostname=MQTT_SERVER)
    publish.single('full_img', payload=file_content, hostname=MQTT_SERVER)


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # cleans each frame 
    rawCapture.truncate()
    rawCapture.seek(0)

    # get ready for motion analysis
    image = frame.array
    grayFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #init the mseError array for 10 frames
    if i < 10:
        init_mse_arr(grayFrame)
        i += 1
        print("Preparing the video stream with %s frames" %i)
    else:
        err = frame_arr(grayFrame)
        MSE = mse(grayStill, grayFrame)
        print(err)
        if abs(err) > motion_filter:
            print('Motion detected - publishing to mqtt')
            pub_message(image, err, MSE)
