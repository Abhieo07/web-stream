import threading
import time
import cv2
import numpy as np
from django.http.response import StreamingHttpResponse, HttpResponse
from django.http import HttpResponseServerError
from django.db import models

# Create your models here.
streamManagerLock = threading.Lock()
streamManagers = {}


class StreamManager:
    active = True
    lastTime = time.time()
    image = None

    def __init__(self, cameraObj):
        self.camera = cameraObj
        url = "https://" + str(cameraObj.system.systemID) + ".relay-la.vmsproxy.com"
        self.stream = cv2.VideoCapture("{url}/web/media/{camID}.webm?auth={auth}".format(url=url,
                                                                                    camID=cameraObj.cam_id,
                                                                                    auth=cameraObj.system.getAuth()))
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 5)

        self.killThread = threading.Thread(target=self.selfTerminate, daemon=True)
        self.lastTime = time.time()
        self.killThread.start()

        self.updateThread = threading.Thread(target=self.update_frame, daemon=True)
        self.updateThread.start()

    def selfTerminate(self):
        while True:
            if time.time() - self.lastTime > 3:
                break
            time.sleep(1)
        self.terminate()

    def terminate(self):
        with streamManagerLock:
            streamManagers.pop(str(self.camera.cam_id))
        self.active = False
        self.stream.release()

    def update_frame(self):
        while self.active:
            ret, image = self.stream.read()
            if ret:
                ret, jpeg = cv2.imencode('.jpg', image)
                self.image = jpeg.tobytes()
            else:
                ret, img = cv2.imencode('.jpg', np.zeros([100, 100, 3], dtype=np.uint8))
                return img.tobytes()
            time.sleep(1/30)

    def get_frame(self):
        self.lastTime = time.time()
        if self.image is None:
            ret, img = cv2.imencode('.jpg', np.zeros([100, 100, 3], dtype=np.uint8))
            return img.tobytes()
        return self.image


def getCameraStream(cameraObj):
    with streamManagerLock:
        if str(cameraObj.cam_id) in streamManagers.keys():
            return streamManagers[str(cameraObj.cam_id)]
        else:
            r = StreamManager(cameraObj)
            streamManagers.update({str(cameraObj.cam_id): r})
            return r


class Camera(models.Model):
    cam_id = models.UUIDField()
    label = models.CharField(max_length=100)

    visible = models.ManyToManyField(CompanyModel, blank=True)

    system = models.ForeignKey(DWCloudSystem, verbose_name="System", on_delete=models.CASCADE)
    profile = models.ManyToManyField(UserProfile, blank=True)

    isPublic = models.BooleanField(default=False)

    def getStream(self):
        def gen():
            stream = getCameraStream(self)
            while True:
                frame = stream.get_frame()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        try:
            return StreamingHttpResponse(gen(), content_type="multipart/x-mixed-replace;boundary=frame")
        except HttpResponseServerError() as e:
            return HttpResponseServerError()

    def getThumbnail(self, height):
        url = "ec2/cameraThumbnail"
        params = {"cameraId": str(self.cam_id), "time": "LATEST", "height": 300, "ignoreExternalArchive": None}

        response = self.system.proxyRequest(url, params=params)
        if response is None:
            time.sleep(3)
            response = self.system.proxyRequest(url, params=params)
            if response is None:
                return HttpResponseServerError()

        return HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers['Content-Type']
        )

    def __str__(self):
        return "{}: {}".format(str(self.system.company_key), str(self.label))