import os
import sys
import time

import cv2
import requests

CAMER_URL = os.environ.get('CAMER_URL', 'http://127.0.0.1:5000/mjpeg/camera/1/feed')
FILEPATH = os.environ.get('FILEPATH', '/home/bat/Video/small.mp4')

def LOG(msg):
    print(msg, file=sys.stderr)

def stream_file(filepath):
    cap = cv2.VideoCapture(filepath)

    if cap.isOpened() is False:
        LOG("Error opening video stream or file")
    else:
        LOG('started>')
        while(cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:
                _, jpeg = cv2.imencode('.jpg', frame)
                files = {'image': jpeg.tostring()}
                rv = requests.post(CAMER_URL, files=files)
            else:
                break
        cap.release()

if __name__ == '__main__':
    STREAM_VIDEO = os.environ.get('STREAM_VIDEO', 'TRUE').upper()
    if STREAM_VIDEO == 'TRUE':
        while True:
            stream_file(FILEPATH)
    else:
        while True:
            time.sleep(10)
