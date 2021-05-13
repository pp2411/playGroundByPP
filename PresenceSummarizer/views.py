from django.shortcuts import render
from .forms import *
import numpy as np
import cv2
import datetime
import face_recognition
from threading import Thread
import sys
from queue import Queue
import time
# Create your views here.
class FileVideoStream:

	def __init__(self, path, queueSize=128):
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		self.stream = cv2.VideoCapture(path)
		self.stopped = False
		# initialize the queue used to store frames read from
		# the video file
		self.Q = Queue(maxsize=queueSize)

	# start a thread to read frames from the file video stream
	def start(self):
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self
	
    # keep looping infinitely
	def update(self):
		while True:
			if self.stopped:
				return
			
			if not self.Q.full():
				(grabbed , frame) = self.stream.read()

				if not grabbed:
					self.stop()
					return
				
				self.Q.put(frame)

	def read(self):
		'''  return next frame in the queue	'''
		return self.Q.get()
    
	def more(self):
		'''  return next frame in the queue'''
		return self.Q.qsize() > 0

	def stop(self):
		''' indicate that the thread should be stopped '''
		self.stopped = True





def findEncodings(imgs):
    ''' Function to return encodings of all the images in the list images '''
    encodes = []
    for img in imgs:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodes.append(encode)
    print("encoded")
    return encodes

def makeTimeStamp(ms):
    sec, ms = divmod(ms, 1000)
    min, sec = divmod(sec, 60)
    hour, min = divmod(min, 60)
    
    return f"{int(hour)}:{int(min)}:{int(sec)}:{int(ms)}"

def scan(name , casePath , vid):
    # casePath = "playGroundByPP"+casePath
    # vid = "playGroundByPP"+vid
    case = face_recognition.load_image_file(casePath)
    result = {"timeIns":[] , "timeOuts":[] , "Duration":""}
    caseEncode = findEncodings([case])[0]
    fvs = FileVideoStream(vid).start()
    fps = int(fvs.stream.get(cv2.CAP_PROP_FPS))
    time.sleep(1.0)
    isHere = False
    dur = 0
    timeIn = ""
    timeOut = ""
    print("Starting Scan...")
    
    lastRead = ""
    while fvs.more():
        wasHere = isHere
        isHere = False
        img = fvs.read()
        try:    
            imgS = cv2.resize(img,(0,0),None,0.25,0.25)
            imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
            
            #   locating faces in the frame
            facesCurr = face_recognition.face_locations(imgS)
            encodesCurr = face_recognition.face_encodings(imgS,facesCurr)

            # compare each face in our current frame with that of test case

            for encode, faceLoc in zip(encodesCurr , facesCurr):
                match = face_recognition.compare_faces([caseEncode],encode)[0]
                faceDis = face_recognition.face_distance([caseEncode],encode)[0]
                # print(faceDis)
                matchIndex = faceDis

                if match:
                    isHere = True
            if isHere:
                dur += 1/fps

            
            if not wasHere and isHere:
                timeI = fvs.stream.get(cv2.CAP_PROP_POS_MSEC) - 4511
                timeIn = makeTimeStamp(timeI)
                print(f" timein: {timeIn}",end="")

            if not isHere and wasHere:
                timeO = fvs.stream.get(cv2.CAP_PROP_POS_MSEC)-4511
                timeOut = makeTimeStamp(timeO)
                print(f"- {timeOut}")
                result["timeIns"].append(timeIn)
                result["timeOuts"].append(timeOut)

        except Exception as e:
             lastRead = makeTimeStamp(timeO)
             break
    
    result['Duration'] = f"{dur} sec"
    result['ExitedAt'] = lastRead
    return result



def presenceSum(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        img = request.FILES.get('img')
        vid = request.FILES.get('vid')
        flag = False
        result = None
        try:
            obj = ScanRequest.objects.create(name = name , img = img , vid = vid)
            result = scan(name , obj.img.path , obj.vid.path )
            result["data"] = zip(result['timeIns'], result['timeOuts'])
            result["Name"] = obj.name
            flag = True
            ScanRequest.objects.filter(id = obj.id).delete()
        except Exception as e:
            print(str(e))
        return render(request , 'PresenceSummarizer/results.html' , { 'flag':flag, 'result':result })
    
    else:
        form = RequestForm()
        return render(request, 'PresenceSummarizer/enterdetails.html', {"form":form})
    


