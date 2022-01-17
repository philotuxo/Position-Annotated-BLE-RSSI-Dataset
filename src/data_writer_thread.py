import sys
sys.path.append("..")
import time
from PyQt5.QtCore import QThread

class DataWriterThread(QThread):
    def __init__(self, name, inQ, guiQ, fileName):
        QThread.__init__(self)
        self.name = name
        self.inQ = inQ
        self.guiQ = guiQ
        self.fileName = fileName
        self.fid = None

        print("DataLogger started.")

    def openFile(self):
        self.fid = open(self.fileName, 'a+')
        if self.fid:
            self.guiQ.put(['O', self.fileName])
        else:
            self.guiQ.put(['F', self.fileName])

    def closeFile(self):
        self.fid.close()

    def run(self):
        # send starting message to GUI
        self.guiQ.put(['S', self.name])
        self.openFile()

        quit = False
        while True:
            # inQueue parser
            while self.inQ.qsize() > 0:
                incoming = self.inQ.get()
                msg = incoming[0]
                if msg == 'Q':
                    # quit
                    quit = True
                    break
                data = incoming[1:]
                if msg == 'L':
                    # log incoming data
                    self.fid.write(str(data) + '\n')
            self.fid.flush()
            if quit:
                break
            time.sleep(0.05)

        self.guiQ.put(['E', self.name])
        print("DataLogger %s ended." % (self.name) )
