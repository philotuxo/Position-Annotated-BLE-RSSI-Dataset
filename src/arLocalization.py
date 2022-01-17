import sys
from os.path import (dirname, abspath)
from pathlib import Path
import inspect

sys.path.append("..")
from lib.arCommon import *
from lib.arViewer_ui import *
from lib.btImageScene import *
from lib.paths import *
import json
import queue
from src.image_grabber_thread import ImageGrabberThread
from src.image_processor_thread import ImageProcessorThread
from src.data_writer_thread import DataWriterThread
from PyQt5 import QtCore, QtWidgets, Qt

lineTrailColor = QtGui.QColor(0,0,0,100)
omittedColor = QtGui.QColor(255,0,0,30)
lineOmittedColor = QtGui.QColor(255,0,0,10)
arrowColor = QtGui.QColor(0,0,0,150)
markerArrowColor = QtGui.QColor(0,0,0,150)

class arLocalizationGui(QtWidgets.QMainWindow):
    def __init__(self, grabQ, procQ, inQ, imQ, writeQ,
                 paramFile, imageFile, markerFile,
                 camFile0 = None, camFile1 = None,
                 timeStartFile = None,
                 outFile = None, kalmanCov = None):

        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)
        self.inQ = inQ
        self.grabQ = grabQ
        self.procQ = procQ
        self.imQ = imQ
        self.writeQ = writeQ

        # create the main ui
        self.ui = Ui_VisualDataViewer()
        self.ui.setupUi(self)

        self.imageScene = btImageScene(self)
        self.pixMap = None
        self.videoFiles = [None, None]

        self.ui.loadImageButton.pressed.connect(self.loadImagePressed)
        self.ui.resetImageButton.pressed.connect(self.resetImagePressed)
        self.ui.loadParametersButton.pressed.connect(self.loadParametersPressed)
        self.ui.loadMarkers.pressed.connect(self.readMarkersPressed)
        self.ui.startDetectionButton.pressed.connect(self.startGrabbing)
        self.ui.stopDetectionButton.pressed.connect(self.stopDetection)
        self.ui.pauseDetectionButton.pressed.connect(self.pauseDetection)
        self.ui.stepDetectionButton.pressed.connect(self.stepDetection)
        self.ui.skipFramesButton.pressed.connect(self.skipFrames)
        self.ui.destinationButton.pressed.connect(self.destinationPressed)
        self.ui.saveImageButton.pressed.connect(self.saveMapVisual)


        self.truthColor = QtGui.QColor(0, 255, 0)
        self.trackColor = QtGui.QColor(0, 0, 0)
        self.ui.alphaSlider.valueChanged.connect(self.alphaSliderChanged)
        self.selectColorPressed(0, self.truthColor)
        self.selectColorPressed(1, self.trackColor)
        self.ui.loadTruthDirButton.pressed.connect(
            self.loadGroundTruthDirPressed)
        self.ui.loadTruthFileButton.pressed.connect(
            self.loadGroundTruthFilePressed)
        self.ui.truthColorBox.pressed.connect(lambda:
            self.selectColorPressed(0)
        )
        self.ui.trackColorBox.pressed.connect(lambda:
            self.selectColorPressed(1)
        )
        self.ui.loadTrackFileButton.pressed.connect(
            self.loadTrackFromFile
        )

        # slider configuration
        self.ui.sliderCovObsOri.valueChanged.connect(self.sliderObsOriChanged)
        self.ui.sliderCovObsPos.valueChanged.connect(self.sliderObsPosChanged)
        self.ui.sliderCovTraOri.valueChanged.connect(self.sliderTraOriChanged)
        self.ui.sliderCovTraPos.valueChanged.connect(self.sliderTraPosChanged)

        # spinbox change
        self.ui.processsizeBox.valueChanged.connect(self.sendBatchSize)

        # combobox selection
        self.ui.cameraSelect0.currentIndexChanged.connect(
            lambda: self.cameraSelectionChanged(0))
        self.ui.cameraSelect1.currentIndexChanged.connect(
            lambda: self.cameraSelectionChanged(1))

        self.ui.reverseCheckBox0.stateChanged.connect(
            lambda: self.reversePressed(0))
        self.ui.reverseCheckBox1.stateChanged.connect(
            lambda: self.reversePressed(1))
        self.reversePressed(0)
        self.reversePressed(1)

        self.ui.calibrationComboBox.currentIndexChanged.connect(
            self.calibrationSelectionChanged
        )

        # parameters
        self.params = {}
        self.params["parity"] = None
        self.params["origin"] = None
        self.params["direction"] = None
        self.params["limits"] = None
        self.params["points"] = [None, None]

        self.markerCoords = {}
        self.markerOri = {}
        self.markers = None
        self.markerVisuals = {}
        self.markerArrowVisuals = {}

        self.posVisuals = []
        self.lineVisuals = []
        self.arrowVisuals = []

        self.segmentVisuals = {}
        self.trackVisuals = []
        self.trackLineVisuals = []

        self.covEllipse = None

        self.paramFile = None
        self.imageFile = None
        self.markerFile = None

        # time offset
        self.timeStampOffset = 0.0

        self.ui.timeStartBox.valueChanged.connect(self.timeStartStampChanged)

        # prepare camera View
        self.cameraMap0 = QtGui.QPixmap()
        self.cameraScene0 = QtWidgets.QGraphicsScene()
        self.ui.cameraView0.setScene(self.cameraScene0)
        self.cameraMap1 = QtGui.QPixmap()
        self.cameraScene1 = QtWidgets.QGraphicsScene()
        self.ui.cameraView1.setScene(self.cameraScene1)

        # prepare map view
        self.ui.imageView.setScene(self.imageScene)
        self.ui.imageView.setStyleSheet("background: transparent")

        # data holders
        self.timerTriggered = False
        self.pThread = None
        self.wThread = None
        self.gThread = [None, None]

        if paramFile:
            self.loadParametersPressed(paramFile)

        if imageFile:
            self.loadImagePressed(imageFile)

        self.timer = Qt.QTimer()
        self.timer.timeout.connect(self.parseQueue)

        # update every 100 ms
        self.timer.start(100)

        self.ui.cameraCheckBox.setChecked(True)
        self.ui.kalmanCheckBox.setChecked(True)
        self.ui.cameraCheckBox.stateChanged.connect(self.sendState)
        self.ui.kalmanCheckBox.stateChanged.connect(self.sendState)

        self.kalmanPars = [0, 0, 0, 0]

        # initializers
        self.fillAvailableSources()
        self.fillAvailableCalibrations()
        self.sliderTraPosChanged()
        self.sliderTraOriChanged()
        self.sliderObsPosChanged()
        self.sliderObsOriChanged()
        self.sendBatchSize()

        if markerFile:
            self.readMarkersPressed(markerFile)

        if not camFile0 == None:
            self.loadVideoPressed(0, videoFile=camFile0)

        if not camFile1 == None:
            self.loadVideoPressed(1, videoFile=camFile1)

        if not timeStartFile == None:
            fid = open(timeStartFile, 'r')
            tS = float(fid.readline().strip())
            fid.close()
            self.ui.timeStartBox.setValue(tS)

        if not outFile == None:
            self.destinationPressed(outFile)

        self.ui.saveTimeButton.pressed.connect(self.saveTimeStamp)

        # self.ui.kalmanCheckBox.setChecked(False)

        self.ui.sliderCovObsPos.setValue(-20)
        self.ui.alphaSlider.setValue(45)
        self.ui.cameraCheckBox.setChecked(False)
        # self.startGrabbing()
        self.ui.closeEndCheckBox.setChecked(True)
        if kalmanCov:
            self.kalmanPars[2] = float(kalmanCov)
            self.sendKalmanPars()


    def alphaSliderChanged(self):
        self.selectColorPressed(0, self.truthColor)
        self.selectColorPressed(1, self.trackColor)

    def setAlphas(self):
        alpha = self.ui.alphaSlider.value()
        self.truthColor.setAlpha(alpha)
        self.trackColor.setAlpha(alpha)
        self.ui.labelAlpha.setText(str(alpha))

    def selectColorPressed(self, index = 0, color = None):
        if color == None:
            dialog = Qt.QColorDialog(self)
            color = dialog.getColor()

        if color == None:
            return

        if index == 0:
            box = self.ui.truthColorBox
            self.truthColor = color
        else:
            box = self.ui.trackColorBox
            self.trackColor = color

        self.setAlphas()
        # color.setAlpha(150)
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Button, color)
        box.setAutoFillBackground(True)
        box.setPalette(pal)
        box.update()

    def loadGroundTruthFilePressed(self, truthFile = None):
        if not truthFile:
            truthFile, dummy = QtWidgets.QFileDialog.\
                getOpenFileName(self,
                                'Open file',
                                "data/test02/segments",
                                'Text File (*.txt)')
        if not truthFile:
            return

        with open(truthFile, 'r') as f:
            self.parseSegments(truthFile)

    def loadGroundTruthDirPressed(self, truthDir = None):
        if not truthDir:
            truthDir = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Directory",
                "data/test02/segments",
                options=QtWidgets.QFileDialog.ShowDirsOnly|
                         QtWidgets.QFileDialog.DontUseNativeDialog
            )

        if truthDir:
            self.log("Parsing directory: %s." %(truthDir))
            for truthFile in os.listdir(truthDir):
                self.parseSegments(truthFile, truthDir)

        if not truthDir:
            self.log("No data loaded.", True)

    def loadTrackFromFile(self):
        for visual in self.trackVisuals:
            self.imageScene.removeItem(visual)
        for visual in self.trackLineVisuals:
            self.imageScene.removeItem(visual)
        self.trackVisuals.clear()
        self.trackLineVisuals.clear()
        tFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                  'Open file',
                                                  pathData,
                                                  'Track Data (*.mbd *.txt)')

        if not tFile:
            return

        # pn = QtGui.QPen()
        # lineTrailColor.setAlpha(255)
        # pn.setColor(lineTrailColor)
        point = False
        oldPoint = False
        with open(tFile, 'r') as f:
            for line in f:
                each = line.strip().split(',')
                if point:
                    oldPoint = point
                point = real2pix(self.params, (float(each[3]),float(each[2])))

                itemPoint = self.imageScene.addPoint(point,'',
                                                     self.trackColor,
                                                     radius = 3)
                if len(self.trackVisuals) > 1:
                    itemLine = self.imageScene.addLine(
                        oldPoint.x(),
                        oldPoint.y(),
                        point.x(), point.y()
                    )

                    self.trackLineVisuals.append(itemLine)
                self.trackVisuals.append(itemPoint)
            self.log ("Data file loaded " + tFile)

    def parseSegments(self, truthFile, truthDir = None):
        fileName = os.path.basename(truthFile)
        uniqName = fileName[:-12]
        if truthDir:
            path = truthDir + "/" + truthFile
        else:
            path = truthFile
        with open(path, 'r') as fid:
            if uniqName in self.segmentVisuals.keys():
                for segment in self.segmentVisuals[uniqName]:
                    for arrowVisual in segment:
                        self.imageScene.removeItem(arrowVisual)
            self.segmentVisuals[uniqName] = []
            for line in fid:
                segment = json.loads(line.strip())
                if not len(segment) == 2:
                    continue
                p1 = real2pix(self.params, (segment[0][1], segment[0][2]))
                p2 = real2pix(self.params, (segment[1][1], segment[1][2]))

                arrowVisuals = self.imageScene.addArrow(
                    p1, p2,
                    QtGui.QColor(self.truthColor),
                    weight=5)
                self.segmentVisuals[uniqName].append(arrowVisuals)

    def saveTimeStamp(self):
        self.procQ.put(['TS'])

    def sendBatchSize(self):
        self.procQ.put(['B', int(self.ui.processsizeBox.text())])

    def timeStartStampChanged(self):
        self.timeStampOffset = float(self.ui.timeStartBox.text())

    def fillAvailableSources(self):
        comboIndex = 1
        self.ui.cameraSelect0.addItem("Video file...")
        self.ui.cameraSelect1.addItem("Video file...")

        self.ui.cameraSelect0.setItemData(0, 0, QtCore.Qt.UserRole - 1)
        self.ui.cameraSelect1.setItemData(0, 0, QtCore.Qt.UserRole - 1)

        self.camDict = getCameras()

        for camID in self.camDict.keys():
            comboIndex += 1
            self.ui.cameraSelect0.addItem("%s (%s)" % (self.camDict[camID][0],
                                                       self.camDict[camID][1]))
            self.ui.cameraSelect0.setItemData(comboIndex, camID,
                                              QtCore.Qt.UserRole)
            self.ui.cameraSelect1.addItem("%s (%s)" % (self.camDict[camID][0],
                                                       self.camDict[camID][1]))
            self.ui.cameraSelect1.setItemData(comboIndex, camID,
                                              QtCore.Qt.UserRole)

    def fillAvailableCalibrations(self):
        default = 'GoPro Linear'
        defaultIndex = None
        counter = 0
        for i in camParameters.keys():
            self.ui.calibrationComboBox.addItem(i,i)
            if i == default:
                defaultIndex = counter
            counter += 1

        if  default in camParameters.keys():
            self.ui.calibrationComboBox.setCurrentIndex(defaultIndex)

    def calibrationSelectionChanged(self):
        key = self.ui.calibrationComboBox.currentData()
        self.procQ.put(('C', key)) # send calibration selection

    def cameraSelectionChanged(self, viewIndex):
        if viewIndex == 0:
            if self.ui.cameraSelect0.currentIndex() == 1:
                self.loadVideoPressed(viewIndex)
            if self.ui.cameraSelect0.currentIndex() > 1:
                self.loadVideoPressed(viewIndex,
                                      self.ui.cameraSelect0.currentData())

            # set the selection to 0
            self.ui.cameraSelect0.setCurrentIndex(0)

        if viewIndex == 1:
            if self.ui.cameraSelect1.currentIndex() == 1:
                self.loadVideoPressed(viewIndex)
            if self.ui.cameraSelect1.currentIndex() > 1:
                self.loadVideoPressed(viewIndex,
                                      self.ui.cameraSelect1.currentData())

            # set the selection to 0
            self.ui.cameraSelect1.setCurrentIndex(0)

    def reversePressed(self, index):
        if not index in [0, 1]:
            return

        # if self.gThread[index]:
        if index == 0:
            if self.ui.reverseCheckBox0.isChecked():
                self.procQ.put(['O', index])
            else:
                self.procQ.put(['O', ' '])

        if index == 1:
            if self.ui.reverseCheckBox1.isChecked():
                self.procQ.put(['O', index])
            else:
                self.procQ.put(['O', ' '])

    def setParityButtonPressed(self):
        if self.params['points'][0] and self.params['points'][1]:
            self.params["parity"] = \
                1 / math.sqrt(
                    (self.params['points'][0].x() -
                     self.params['points'][1].x()) ** 2 + \
                    (self.params['points'][0].y() -
                     self.params['points'][1].y()) ** 2)

            self.updateParameters()

    def setLimitsPressed(self):
        if self.params["parity"] \
                and self.params["origin"] \
                and self.params["direction"] \
                and all(self.params["points"]):
            self.params["limits"] = (
                pix2real(self.params, self.params['points'][0]),
                pix2real(self.params, self.params['points'][1]))
            # self.imageScene.placeParameters()
            self.updateParameters()

    def resetImagePressed(self):
        if self.imageFile:
            self.log("Image reset.", 0)

        self.imageScene.removeVisuals()
        self.removeMarkerVisuals()

        self.imageScene.clear()
        self.imageFile = None

    def readMarkersPressed(self, markerFile=None):
        if not markerFile:
            markerFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                      'Open file',
                                                                      './data/',
                                                                      'Images (*.dat)')
        if not markerFile:
            return

        self.markerFile = markerFile
        self.markers = readMarkerConfiguration(markerFile)
        self.log("Loading markers: %s." % (markerFile), 1)

        self.putMarkerVisuals()
        self.startDetection()

    def updateCamera(self, index, frameCount, time, frame):
        if index == 0:
            self.cameraMap0 = QtGui.QPixmap(frame)
            self.cameraScene0.clear()
            self.cameraScene0.addPixmap(self.cameraMap0)
            self.ui.labelTime0.setText(str(frameCount))
        else:
            self.cameraMap1 = QtGui.QPixmap(frame)
            self.cameraScene1.clear()
            self.cameraScene1.addPixmap(self.cameraMap1)
            self.ui.labelTime1.setText(str(frameCount))

    def loadVideoPressed(self, viewIndex, videoFile=None):
        if videoFile == None:
            videoFile, dummy = QtWidgets.QFileDialog.getOpenFileName(
                self,
                'Open file',
                "./data/",
                'Videos (*.avi *.mpg *.mkv *.mp4)')
        if videoFile == None:
            self.log("Video file not set!", -1)
            return

        # set the combobox contents
        if viewIndex == 0:
            if type(videoFile) == int:
                self.ui.cameraSelect0.setItemText(0,
                                                  "Selected: %s" % (
                                                  self.camDict[videoFile][1]))
            else:
                self.ui.cameraSelect0.setItemText(0,
                                                  "Selected: ...%s" % (
                                                  videoFile[-25:]))
        if viewIndex == 1:
            if type(videoFile) == int:
                self.ui.cameraSelect1.setItemText(0,
                                                  "Selected: %s" % (
                                                  self.camDict[videoFile][1]))
            else:
                self.ui.cameraSelect1.setItemText(0,
                                                  "Selected: ...%s" % (
                                                  videoFile[-25:]))

        self.videoFiles[viewIndex] = videoFile
        self.log("Setting video file: %s." % (videoFile), 1)

    def startWriteThread(self, writeFile):
        if not self.wThread:
            self.wThread = DataWriterThread(
                'Writer', self.writeQ, self.inQ, writeFile)
            self.wThread.start()
            if not self.wThread:
                return
            self.ui.destinationButton.setText("Stop export")
            self.log("Starting Data Writer: %s" % (writeFile))

    def stopWriteThread(self):
        if self.wThread:
            self.writeQ.put(['Q'])
            self.ui.destinationButton.setText('Start export')
            self.wThread.wait()
            self.wThread = None
            self.log("Stopping Data Writer.")

    def destinationPressed(self, writeFile=None):
        if not self.wThread:
            if writeFile == None:
                writeFile, dummy = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                         'Save file',
                                                                         "./data/",
                                                                         'Data (*.csv)')
            if not writeFile:
                self.log("Data file not set!", -1)
                return

            self.log("Setting video file: %s." % (writeFile), 1)
            self.startWriteThread(writeFile)
        else:
            self.stopWriteThread()

    def saveMapVisual(self, imageFile = None):

        if not imageFile:
            imageFile, dummy = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    'Save file',
                                                    os.path.expanduser("~"),
                                                    'Images '
                                                    ' (*.png *.xpm *.jpg)')
        if not imageFile:
            return

        self.imageScene.saveImage(imageFile)

    def loadImagePressed(self, imageFile=None):
        if not imageFile:
            imageFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                     'Open file',
                                                                     pathMap,
                                                                     'Images (*.png *.xpm '
                                                                     '*.jpg)')
        if not imageFile:
            return

        self.imageFile = imageFile
        with open(imageFile, 'r') as f:
            try:
                self.imageFile = imageFile
                # self.ui.loadBeaconsButton.setDisabled(False)
                # say that an image is loaded
                self.log("Loading image: %s." % (imageFile))
            except:
                self.log("Problem with image file: %s." % (self.imageFile), -1)
                self.imageFile = None
            finally:
                self.updateImage()
                # self.imageScene.putVisuals()

    def toggleSliders(self, on):
        self.ui.sliderCovTraPos.setEnabled(on)
        self.ui.sliderCovObsPos.setEnabled(on)
        self.ui.sliderCovTraOri.setEnabled(on)
        self.ui.sliderCovObsOri.setEnabled(on)

    def sliderTraPosChanged(self):
        val = round(10 ** (self.ui.sliderCovTraPos.value() / 10.0), 3)
        self.kalmanPars[0] = val
        self.ui.labelTraPos.setText(str(val))
        self.sendKalmanPars()

    def sliderTraOriChanged(self):
        val = round(10 ** (self.ui.sliderCovTraOri.value() / 10.0), 3)
        self.kalmanPars[1] = val
        self.ui.labelTraOri.setText(str(val))
        self.sendKalmanPars()

    def sliderObsPosChanged(self):
        val = round(10 ** (self.ui.sliderCovObsPos.value() / 10.0), 3)
        self.kalmanPars[2] = val
        self.ui.labelObsPos.setText(str(val))
        self.sendKalmanPars()

    def sliderObsOriChanged(self):
        val = round(10 ** (self.ui.sliderCovObsOri.value() / 10.0), 3)
        self.kalmanPars[3] = val
        self.ui.labelObsOri.setText(str(val))
        self.sendKalmanPars()

    def sendKalmanPars(self):
        if any(x is None for x in self.kalmanPars):
            return

        if self.pThread:
            self.procQ.put(['A', self.kalmanPars])

    def sendState(self):
        if self.pThread:
            if self.ui.cameraCheckBox.isChecked():
                self.procQ.put(['T'])
            else:
                self.procQ.put(['F'])

            if self.ui.kalmanCheckBox.isChecked():
                self.toggleSliders(True)
                self.procQ.put(['K'])
            else:
                self.toggleSliders(False)
                self.procQ.put(['M'])

    def startDetection(self):
        # this should be automaticly started
        if not self.markers:
            self.log("Marker configuration missing!", -1)
            return

        if self.pThread:
            self.log("Detection already running.", -1)
            return

        self.log("Detection initializing.")
        self.pThread = ImageProcessorThread('Processor',
                                            self.grabQ,
                                            self.procQ,
                                            self.inQ,
                                            self.imQ,
                                            self.markers,
                                            self.kalmanPars)

        self.pThread.start()

    def startGrabbing(self):
        # tell the grabber(s) start grabbing
        if all(x is None for x in self.videoFiles):
            self.log("Video file(s) missing!", -1)
            return

        self.sendState()

        if self.videoFiles[0] is not None:
            self.gThread[0] = ImageGrabberThread(0,
                                                 self.grabQ[0],
                                                 self.inQ,
                                                 self.imQ[0],
                                                 self.procQ,
                                                 self.videoFiles[0])
            self.gThread[0].start()

        if self.videoFiles[1] is not None:
            self.gThread[1] = ImageGrabberThread(1,
                                                 self.grabQ[1],
                                                 self.inQ,
                                                 self.imQ[1],
                                                 self.procQ,
                                                 self.videoFiles[1])

            self.gThread[1].start()

    def stopDetection(self):
        if self.pThread:
            self.log("Manually ending detection.")
            if self.gThread[0]:
                self.grabQ[0].put(['Q'])
                self.gThread[0].wait()
                self.gThread[0] = None
            if self.gThread[1]:
                self.grabQ[1].put(['Q'])
                self.gThread[1].wait()
                self.gThread[1] = None

    def pauseDetection(self):
        if self.pThread:
            self.log("Toggling pause.")
            if self.gThread[0]:
                self.grabQ[0].put(['P'])
            if self.gThread[1]:
                self.grabQ[1].put(['P'])

    def stepDetection(self):
        if self.pThread:
            self.log(("Step forward."))
            if self.gThread[0]:
                self.grabQ[0].put(['T'])
            if self.gThread[1]:
                self.grabQ[1].put(['T'])

    def skipFrames(self):
        if self.pThread:
            size = int(self.ui.skipsizeBox.text())
            self.log(("Skip %s frames." % size))
            if self.gThread[0]:
                self.grabQ[0].put(['S', size])
            if self.gThread[1]:
                self.grabQ[1].put(['S', size])

    def parseQueue(self):
        # trigger, if False don't continue
        if self.timerTriggered:
            return

        self.timerTriggered = True
        # flush it
        while self.inQ.qsize() > 0:
            data = self.inQ.get()
            msg = data[0]
            if msg == 'K':
                # Single Coordinate
                self.updateCoordinates('K', data[3], data[4])
            if msg == 'C':
                self.updateCovariances(data[4][0], data[4][1])
            if msg == 'M':
                # Multiple Coordinates
                self.updateCoordinates('M', data[3], data[4])
            # Info Message
            if msg == 'S':
                self.log("Thread %s: Starting." % (data[1]), 1)
            if msg == 'E':
                self.log("Thread %s: Ending." % (data[1]), 1)
            if msg == 'F':
                # camNo, frameCount, tstamp, cameraMap
                self.updateCamera(data[1], data[2], data[3], data[4])
            if msg == 'TS':
                self.ui.timeStampBrowser.append(str(
                    data[1] + self.ui.timeStartBox.value())
                )
            # processor says quit
            if msg == 'Q':
                if self.ui.closeEndCheckBox.isChecked():
                    self.close()

        # make the function available again
        self.timerTriggered = False

    def updateCovariances(self, coords, sigma):
        E = np.linalg.eig(sigma)
        U = E[1]  # rotation matrix
        alpha = np.arctan(U[0][0] / U[0][1])

        pixCoords = real2pix(self.params, (coords[0], coords[1]))
        pixCov = real2pix(self.params, (
            np.sqrt(sigma[1, 1]), np.sqrt(sigma[0, 0])))

        dimmedBrush = QtGui.QBrush()
        dimmedBrush.setStyle(1)  # RadialGradient pattern
        dimmedBrush.setColor(QtGui.QColor(0, 0, 255, 15))

        dimmedPen = QtGui.QPen()
        dimmedPen.setColor(QtGui.QColor(0, 0, 255, 15))

        self.imageScene.removeItem(self.covEllipse)

        self.covEllipse = QtWidgets.QGraphicsEllipseItem(
            pixCoords.x() - pixCov.x() / 2,
            pixCoords.y() - pixCov.y() / 2,
            pixCov.x(),
            pixCov.y())

        self.covEllipse.setTransformOriginPoint(
            pixCoords.x(),
            pixCoords.y())

        self.covEllipse.setRotation(alpha * 180)

        self.imageScene.addItem(self.covEllipse)

        self.covEllipse.setBrush(dimmedBrush)
        self.covEllipse.setPen(dimmedPen)

    def updateCoordinates(self, poseType, timeStamp, poses):
        # dim the latest visuals
        if len(self.posVisuals) > 0:
            latestPos = self.posVisuals[-1]
            for visual in latestPos:
                br = visual.brush()
                pn = visual.pen()
                clr = br.color()
                clr.setAlpha(clr.alpha()/5)
                br.setColor(clr)
                pn.setColor(clr)
                visual.setBrush(br)
                visual.setPen(pn)

        # keep the old visuals
        while len(self.posVisuals) > self.ui.trailsBox.value():
            latestPos = self.posVisuals.pop(0)
            # remove old visuals
            for visual in latestPos:
                self.imageScene.removeItem(visual)

        for aVisual in self.arrowVisuals:
            for arrowParts in aVisual:
                self.imageScene.removeItem(arrowParts)

        for lVisual in self.lineVisuals:
            self.imageScene.removeItem(lVisual)

        # self.posVisuals.clear()
        self.lineVisuals.clear()
        self.arrowVisuals.clear()

        if poseType == 'K':
            coords = poses[0]  # poses
            arrowEnd = poses[1]  # arrow ends

            if self.wThread:
                self.writeQ.put(['L',
                                 self.timeStampOffset + float(timeStamp),
                                 poses[0]])

            # add new visual
            coords = real2pix(self.params, (coords[0], coords[1]))
            arrowCoords = real2pix(self.params, (arrowEnd[0], arrowEnd[1]))

            visual = self.imageScene.addPoint(coords, "",
                                              self.trackColor,
                                              radius = 3)

            orientArrow = self.imageScene.addArrow(
                coords,
                arrowCoords,
                arrowColor)

            self.posVisuals.append([])
            self.posVisuals[-1].append(visual)
            self.arrowVisuals.append(orientArrow)

        if poseType == 'M':
            ids = poses[0]
            positions = poses[1]
            orientations = poses[2]
            arrowCoords = poses[3]
            show = poses[4]

            if self.wThread:
                for index in range(len(ids)):
                    self.writeQ.put(
                        ['L',
                         self.timeStampOffset + float(timeStamp),
                         positions[index],
                         orientations[index],
                         ids[index]]
                    )

            self.posVisuals.append([])
            for i in range(len(ids)):
                id = ids[i]
                position = positions[i]
                arrows = arrowCoords[i]

                # add new visual
                pixCoords = real2pix(self.params, (position[0], position[1]))
                pixArrows = real2pix(self.params, (arrows[0], arrows[1]))


                if show[i] == 1:
                    visual = self.imageScene.addPoint(pixCoords,
                                                      "",
                                                      self.trackColor,
                                                      radius = 3)
                    lineVisual = self.imageScene.addLine(
                        pixCoords.x(),
                        pixCoords.y(),
                        self.markerCoords[id].x(),
                        self.markerCoords[id].y(),
                        lineTrailColor)

                    arrowVisual = self.imageScene.addArrow(
                        pixCoords,
                        pixArrows,
                        lineTrailColor)

                    self.posVisuals[-1].append(visual)
                    self.lineVisuals.append(lineVisual)
                    self.arrowVisuals.append(arrowVisual)

                else:
                    if self.ui.omittedCheckBox.isChecked():
                        visual = self.imageScene.addPoint(pixCoords,
                                                          "",
                                                          omittedColor,
                                                          radius = 3)

                        lineVisual = self.imageScene.addLine(
                            pixCoords.x(),
                            pixCoords.y(),
                            self.markerCoords[id].x(),
                            self.markerCoords[id].y(),
                            lineOmittedColor)

                        arrowVisual = self.imageScene.addArrow(
                            pixCoords,
                            pixArrows,
                            lineOmittedColor)

                        self.posVisuals[-1].append(visual)
                        self.lineVisuals.append(lineVisual)
                        self.arrowVisuals.append(arrowVisual)

    def putMarkerVisuals(self):
        if not self.markers or not len(self.params) > 0:
            return

        for id in self.markers.keys():
            self.markerCoords[id] = real2pix(self.params,
                                             (self.markers[id][0][0],
                                              self.markers[id][0][1])
                                             )

            theta = self.markers[id][1][0]
            R = rotMat(self.markers[id][1])

            offset = np.matrix([0, 0, .4]).T
            offset_rot = R * offset
            arrowEnd = offset_rot.T + self.markers[id][0]
            arrowEndPix = real2pix(self.params,(arrowEnd[0,0], arrowEnd[0,1])
                                   )
            self.markerOri[id] = self.markers[id][1][2]
            markerVisual = self.imageScene.addPoint(
                self.markerCoords[id],
                str(id),
                QtGui.QColor(255, 255, 255),
                penWeight=1,
                penColor=QtGui.QColor(50, 50, 50)
                )

            self.markerVisuals[id] = markerVisual

            markerArrowVisual = self.imageScene.addArrow(
                self.markerCoords[id],
                arrowEndPix,
                markerArrowColor)

            self.markerArrowVisuals[id] = markerArrowVisual


    def removeMarkerVisuals(self):
        for id in self.markerVisuals.keys():
            self.imageScene.removeItem(self.markerVisuals[id])
            self.imageScene.removeItem(self.markerArrowVisuals[id])

    def setOpacity(self, opacity):
        newImage = QtGui.QImage(self.frame.size(), QtGui.QImage.Format_ARGB32)
        newImage.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(newImage)
        painter.setOpacity(opacity)
        painter.drawImage(QtCore.QRect(
            0, 0, self.frame.width(), self.frame.height()), self.frame)
        return newImage

    def updateImage(self):
        if not self.imageFile:
            return
        self.frame = QtGui.QImage(self.imageFile)

        # check image size and save if necessary

        self.log("Image loaded: %s." % (self.imageFile), 1)

        self.frame = self.setOpacity(.4)
        self.pixMap = QtGui.QPixmap.fromImage(self.frame)
        self.imageScene.setImageSize(self.frame.size())
        self.imageScene.addPixmap(self.pixMap)

        # self.imageScene.putVisuals()
        # self.putMarkerVisuals()
        self.imageScene.update()

    def log(self, logThis, type=0):
        if type == -1:
            self.ui.logBrowser.append("<font ""color=red>%s</font>" % (logThis))
            return
        if type == 1:
            self.ui.logBrowser.append("<font ""color=green>%s</font>" % (
                logThis))
            return
        self.ui.logBrowser.append(logThis)

    def loadParametersPressed(self, parFile=None):
        if not parFile:
            parFile, dummy = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                   'Open file',
                                                                   pathConf,
                                                                   'Parameters (*.par)')

        if not parFile:
            return
        try:
            with open(parFile, 'r') as f:
                tempParams = json.load(f)
                self.params["origin"] = QtCore.QPoint(tempParams["origin"][0],
                                                      tempParams["origin"][1])
                self.params["direction"] = (tempParams["direction"][0],
            	                            tempParams["direction"][1],
            	                            tempParams["direction"][2],
            	                            tempParams["direction"][3])
                self.params["limits"] = ((tempParams["limits"][0],
                                          tempParams["limits"][1]),
                                         (tempParams["limits"][2],
                                          tempParams["limits"][3]))
                self.params["parity"] = tempParams["parity"]
                self.log("Parameters loaded: %s." % (parFile), 1)
        except:
            self.log("Incompatible File: %s." % (parFile))
        finally:
            # self.imageScene.putVisuals()
            self.updateImage()

    def run(self):
        self.show()
        self.qt_app.exec_()

    def closeEvent(self, QCloseEvent):
        self.grabQ[1].put(['Q'])
        self.grabQ[0].put(['Q'])
        self.procQ.put(['Q'])
        del self.imageScene


def main():
    print("Alternative Usage:\n \
    <command> <parameters file> <image file> <marker configuration file>")
    paramFile = None
    imageFile = None
    markerFile = None
    camFile0 = None
    camFile1 = None
    timeFile = None
    outFile = None
    kalmanCov = None

    imQ = [queue.Queue(), queue.Queue()]
    guiQ = queue.Queue()
    grabQ = [queue.Queue(), queue.Queue()]
    procQ = queue.Queue()
    writeQ = queue.Queue()

    if len(sys.argv) > 1:
        paramFile = sys.argv[1]
    if len(sys.argv) > 2:
        imageFile = sys.argv[2]
    if len(sys.argv) > 3:
        markerFile = sys.argv[3]
    if len(sys.argv) > 4:
        camFile0 = sys.argv[4]
    if len(sys.argv) > 5:
        camFile1 = sys.argv[5]
    if len(sys.argv) > 6:
        timeFile = sys.argv[6]
    if len(sys.argv) > 7:
        outFile = sys.argv[7]
    if len(sys.argv) > 8:
        kalmanCov = sys.argv[8]

    app = arLocalizationGui(grabQ, procQ, guiQ, imQ, writeQ,
                            paramFile, imageFile, markerFile,
                            camFile0, camFile1, timeFile, outFile,
                            kalmanCov)
    app.run()


if __name__ == '__main__':
    main()
