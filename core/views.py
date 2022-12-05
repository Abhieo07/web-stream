import gzip
from time import sleep
import time
from django.conf import settings
import threading
from django.core.files.base import ContentFile
from django.http.response import StreamingHttpResponse
import cv2
from django.contrib import messages
from django.shortcuts import render, HttpResponse,redirect
from django.http import JsonResponse
from .models import AjaxField

import numpy as np
import face_recognition
import os
from random import randint

# Create your views here.


#-------------import the saved pictures---------

path=os.path.join(settings.MEDIA_ROOT, "profile_images")
images=[] # list to store images
classNames=[] #list to store names


#-----Saving the picture at start-------------

def savePicture(image,num):
    return cv2.imwrite(r"C:\Users\Dell\Desktop\Project\face_rec\imageTest\image%04i.jpg" %num,image)

#-------------------------------ENCODING----------------------------------

num = randint(1,10)

class FaceModel(object):

    #lastTime = time.time()
    video = cv2.VideoCapture(0)
    stopped = False

    def __init__(self):
        #importing images
        # print("Importing images")
        # myList=os.listdir(path)
        # for cls in myList:
        #     curImg=cv2.imread(f'{path}/{cls}')
        #     images.append(curImg)
        #     classNames.append(os.path.splitext(cls)[0])

        # #encoding
        # self.encodeListKnow=FaceModel.findEncodings(images)
        # print('Encoding Complete')
    
        #self.video = cv2.VideoCapture(0)
        # self.killThread = threading.Thread(target=self.__del__(), args=())
        # self.lastTime = time.time()
        # self.killThread.start()
        if not self.stopped:
            (self.grabbed, self.frame) = self.video.read()
        else:
            self.video.release()
            cv2.destroyAllWindows()
        #self.stopped = False
        threading.Thread(target=self.update, args=()).start()

    # def selfTerminate(self):
    #     while True:
    #         if time.time() - self.lastTime > 10:
    #             break
    #         time.sleep(1)
    #     self.video.release()

    #def __del__(self):
        # while not self.stopped:
        #     if time.time() - self.lastTime > 30: 
        #         break
        #     time.sleep(1)
        # self.stopped = True
        #self.video.release()

    # def findEncodings(images):
    #     encodeList = []
    #     for img in images:
    #         img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    #         encode=face_recognition.face_encodings(img)[0]
    #         encodeList.append(encode)
    #     return encodeList

    def get_frame(self):
        image = self.frame
        image = cv2.flip(image,1)
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    # def prediction(self):
    #     while True:
    #         img = self.frame
    #         #img = cv2.flip(img,1)
    #         imgS=cv2.resize(img,(0,0),None,0.25,0.25)
    #         imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    #         facesCurFrame=face_recognition.face_locations(imgS)
    #         encodesCurFrame=face_recognition.face_encodings(imgS)

    #         for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
    #             matches = face_recognition.compare_faces(self.encodeListKnow,encodeFace)
    #             faceDis = face_recognition.face_distance(self.encodeListKnow,encodeFace)
    #             print("face distance: ",faceDis)
    #             matchIndex=np.argmin(faceDis)
                
    #             return matches[matchIndex], classNames[matchIndex]
           

    def raw(self):
        return self.frame

    def update(self):
        while not self.stopped:
            if not self.grabbed:
                self.stopped = True
                break
            else:
                (self.grabbed, self.frame) = self.video.read()
        # while True:
        #     (self.grabbed, self.frame) = self.video.read()
                  

def gen(camera):
    Timed = time.time()
    stopped = camera.stopped
    while not stopped:
        if time.time() - Timed > 7:
            stopped = True
            camera.video.release()
            cv2.destroyAllWindows()
            break
        else:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def home(request):
    try:
        return StreamingHttpResponse(gen(FaceModel()), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
       
    #     if success == True:
    #         cam.__del__()
    #         messages.info(request,"Face is matched")
    #         #print("Face is matched")
    #         #return HttpResponse("image will not be saved")
    #     elif success == False:
    #         cam.__del__()
    #         messages.info(request,"Face is not matched")
           # print("Face is not matched")
            #return HttpResponse("image will be saved")
    # if success == True:
    #     cam.__del__
    #     return HttpResponse("Face found")
    # elif success == False:
    #     cam.__del__
    #     return HttpResponse("not found will be saved")
    return render(request,"core/home.html")
    
def get_response(request):
    # timer = time.time()
    Images = []
    ClassNames =[]

    cam = FaceModel()
    #print(success,name)
    if request.method == 'GET': #and success == False
        curFrame = cam.get_frame()
        img = ContentFile(curFrame)

        myList=os.listdir(path)
        for cls in myList:
            curImg=cv2.imread(f'{path}/{cls}')
            Images.append(curImg)
            ClassNames.append(os.path.splitext(cls)[0])

        encodeListKnow=findEncodings(Images)
        Img = cam.raw()

        success,name = prediction(Img,encodeListKnow,ClassNames)
        #success,name = cam.prediction()
        
        #print(encodeListKnow)
        #print(curFrame)
        if success == False:
            img_model = AjaxField.objects.get(name='mannu')
            img_model.picture.save(name+'.jpg',img)
            messages.info(request, "Face not matched")
            #if time.time() - timer >10:
                #cam.__del__()
            return HttpResponse("image will be saved")
        elif success == True:
            print("Face is matched")
            messages.info(request, "Face matched")
            # if time.time() - timer >10:
                #cam.__del__()
            return HttpResponse("image will not be saved")
        else:
            print("Some issue")
            return HttpResponse("Some internal issue")
    return render(request,"core/home.html")

#===================will use in def get_response================
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def prediction(img,encodeListKnow,classNames):
    while True:
        #img = cv2.flip(img,1)
        imgS=cv2.resize(img,(0,0),None,0.25,0.25)
        imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

        facesCurFrame=face_recognition.face_locations(imgS)
        encodesCurFrame=face_recognition.face_encodings(imgS)

        for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnow,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnow,encodeFace)
            print("face distance: ",faceDis)
            matchIndex=np.argmin(faceDis)
            
            return matches[matchIndex], classNames[matchIndex]