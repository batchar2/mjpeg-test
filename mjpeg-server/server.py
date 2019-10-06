import os
import sys
import time
import base64
import datetime
import requests
import threading

import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify

SERVER_PORT = int(os.environ.get('SERVER_PORT', '5000'))
IMAGE_CACHED_SECONDS = int(os.environ.get('IMAGE_CACHED_SECONDS', '20'))
RESTART_CAMERA_SECONDS = int(os.environ.get('RESTART_CAMERA_SECONDS', '60'))
#RESTART_CAMERA_URL = os.environ.get('RESTART_CAMERA_URL', 'http://127.0.0.1:3000/api/cameras/restart')

class MjpegCamera:
    def __init__(self, camid, default_image):
        self._lock = threading.Lock()

        self._camid = camid
        self._encoded_image = None
        self._date_recv_image = datetime.datetime.now()
        self._default_image = self._encode_jpeg(default_image, 50)

    def _encode_jpeg(self, image, quality):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        ret, jpeg = cv2.imencode('.jpg', image, encode_param)
        return jpeg.tobytes()

    def get_frame(self):
        with self._lock:
            delta = datetime.datetime.now() - self._date_recv_image
            if self._encoded_image is not None and delta.seconds <= IMAGE_CACHED_SECONDS:
                return self._encoded_image
            return self._default_image

    def set_frame(self, image):
        with self._lock:
            self._encoded_image = self._encode_jpeg(image, 50)
            self._date_recv_image = datetime.datetime.now()

    @property
    def camid(self):
        return self._camid

    @property
    def date_updated(self):
        with self._lock:
            return self._date_recv_image

class RegisterCameras:
    def __init__(self, default_image_path):
        self._default_image = cv2.imread(default_image_path)
        self._cameras = {}
        self._lock = threading.Lock()

    def get_camera(self, camid):
        with self._lock:
            if not camid in self._cameras:
                self._cameras[camid] = MjpegCamera(camid, self._default_image)
            return self._cameras[camid]

    @property
    def cams(self):
        with self._lock:
            return self._cameras




cameras = RegisterCameras('./no-image.png')

#cameras = RegisterCameras('/src/no-image.png')
app = Flask(__name__)

@app.route('/')
def index():
    return """<html>
          <head>
            <title>Video Streaming Demonstration</title>
          </head>
          <body>
            <h1>Video Streaming Demonstration</h1>
            <img id="bg" src="/camera/1/feed">
          </body>
        </html>
    """
    return render_template('index.html')

@app.route('/mjpeg/camera/<int:camid>/feed', methods=['GET', 'POST'])
def video_feed(camid):
    def generate_mjpeg_frame(camera):
        while True:
            time.sleep(0.080)
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cam = cameras.get_camera(camid)
    if request.method == 'GET':
        resp = Response(generate_mjpeg_frame(cam), mimetype='multipart/x-mixed-replace; boundary=frame')
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0'
        resp.headers['Connection']    = 'close'
        resp.headers['Pragma']        = 'no-cache'
        return resp
    else:
        print("[info] recv camera image {}".format(camid), file=sys.stderr)
        file = request.files['image']
        data = file.read()
        nparr = np.fromstring(data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR) # cv2.IMREAD_COLOR in OpenCV   CV_LOAD_IMAGE_COLOR 3.1
        cam.set_frame(image)
        return jsonify(success=True)

@app.route('/mjpeg/camera/status/<int:camid>', methods=['GET',])
def camera_status(camid):
    """ Возврат статуса о состоянии камеры """
    camera = cameras.get_camera(camid)
    date_updated = camera.date_updated
    delta = datetime.datetime.now() - date_updated
    print('camid>', camid, datetime.datetime.now(), date_updated, delta)
    if delta.seconds <= RESTART_CAMERA_SECONDS:
        return jsonify(started=True)
    return jsonify(started=False)

# class CameraControl(threading.Thread):
#     def __init__(self, interval):
#         self._interval = interval
#         super().__init__()
#
#     def run(self):
#         while True:
#             time.sleep(self._interval)
#             print("run>> ", cameras.cams)
#             cams = cameras.cams
#             for id, cam in cams.items():
#                 print("    camid >> ", id)
#                 date_updated = cam.date_updated
#
#                 delta = datetime.datetime.now() - date_updated
#                 if delta.seconds >= RESTART_CAMERA_SECONDS:
#                     url = '{}/{}'.format(RESTART_CAMERA_URL, id)
#                     r = requests.post(url)
#                     print("        send to ", id, r)
#



if __name__ == '__main__':
    #camctrl = CameraControl(RESTART_CAMERA_SECONDS)
    #camctrl.start()
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)
