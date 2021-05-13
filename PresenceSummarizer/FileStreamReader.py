from threading import Thread
import sys
import cv2
from queue import Queue
import time

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

    