import sys
sys.path.append("..")
from lib.arCommon import *
import time
from PyQt5.QtCore import QThread

class ImageGrabberThread(QThread):
    def __init__(self, no, inQ, guiQ, imQ, procQ, fileName):
        QThread.__init__(self)
        self.no = no
        self.guiQ = guiQ
        self.inQ = inQ
        self.imQ = imQ
        self.procQ = procQ
        self.fileName = fileName
        self.captured = None
        self.fps = None
        self.timeOffset = 0
        self.timeStamp = None
        self.frameCount = 0
        # decide if the video is over (3 seconds)
        self.isOverCounter = 0

        if type(self.fileName) == int:
            self.typeVideo = False
            self.procQ.put(['L'])
        else:
            self.typeVideo = True
            self.procQ.put(['H'])

        print("ImageGrabber %s started." % (self.no) )

    # queue message syntax
    # message type, time, data


    def run(self):
        paused = False
        step = False
        skipSize = 0
        # send starting message to GUI
        self.guiQ.put(['S', self.no])

        # Start capturing images for calibration
        self.captured = cv2.VideoCapture(self.fileName)
        # self.captured.set(3, 800)
        # self.captured.set(4, 600)

        self.captured.open(self.fileName)
        self.fps = self.captured.get(cv2.CAP_PROP_FPS)
        self.durationExp = 1.0/self.fps
        while True:
            # inQueue parser
            if self.inQ.qsize() > 0:
                incoming = self.inQ.get()
                msg = incoming[0]
                if msg == 'Q':
                    # quit
                    break
                if msg == 'P':
                    # pause
                    if paused:
                        paused = False
                    else:
                        paused = True
                if msg == 'T':
                    # step
                    step = True
                    paused = False
                if msg == 'S':
                    # skip
                    skipSize = incoming[1]

            if paused and not skipSize > 0:
                time.sleep(time_wait)
            else:
                if self.typeVideo:

                    if skipSize > 0:
                        self.captured.set(cv2.CAP_PROP_POS_FRAMES,
                                          self.frameCount + skipSize)
                        skipSize = 0

                    ret, frame = self.captured.read()
                    if ret:
                        self.isOverCounter = 0
                        self.frameCount = self.captured.get(cv2.CAP_PROP_POS_FRAMES)

                        self.timeStamp = np.round(self.frameCount * \
                                         self.durationExp, 2)

                    if step:
                        paused = True
                        step = False

                else:
                    ret, frame = self.captured.read()
                    self.timeStamp = time.time()

                if ret:
                    # wait if image queue is full (10 images)
                    while self.imQ.qsize() > 10:
                        time.sleep(time_wait)
                    # send raw image with count and time
                    self.imQ.put([self.no, self.frameCount, self.timeStamp,  frame ])
                else:
                    self.isOverCounter += 1
                    if self.isOverCounter > self.fps * 3:
                        print("ImageGrabber %s hit the error limit." % (
                            self.no))
                        break

        self.captured.release()
        # say ending
        self.guiQ.put(['E', self.no])
        self.procQ.put(['E', self.no])

        print("ImageGrabber %s ended." % (self.no) )
