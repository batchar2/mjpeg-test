import cv2
import requests


image = cv2.imread('/home/bat/Pictures/kolcovo.jpg')
_, jpeg = cv2.imencode('.jpg', image)
# rv = requests.post('http://127.0.0.1:5000/camera/1/feed', files={'image': jpeg.tostring()})
# print(rv)

#files = {'image': open('/home/bat/Pictures/kolcovo.jpg', 'rb')}
files = {'image': jpeg.tostring()}
rv = requests.post('http://127.0.0.1:5000/mjpeg/camera/1/feed', files=files)
print(rv)
