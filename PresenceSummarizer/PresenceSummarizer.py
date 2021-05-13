import cv2
import numpy as np 
import face_recognition
import os
from datetime import datetime
from filevideostream import *

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


if __name__ == '__main__':
    case = 'Faces\Bill Gates.jfif'
    name = "Bill"
    vid = "Video\WIN_20210511_18_10_55_Pro.mp4"
    result  = scan(name, case, vid)
    print(result['Duration'])
    if(len(result['ExitedAt'])):
        print(f"Exited at {result['ExitedAt']}.\n Could not read video after this time.")