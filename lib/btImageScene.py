from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import Qt
from .colors import rgb2int
import os
from lib.paths import *
import math


def real2pix(params, coord):
    # take the real coordinates of a point, convert it to pixel coordinates

    if params["direction"] and \
        params["origin"] and \
        params["parity"]:

        # check if
        x_pix = round(params["origin"].x() + \
            coord[params["direction"][0]] / params["parity"] * params[
                    "direction"][2])
        y_pix = round(params["origin"].y() + \
            coord[params["direction"][1]] / params["parity"] * params[
                    "direction"][3])

        return QtCore.QPoint(x_pix, y_pix)
    else:
        return QtCore.QPoint(0,0)

def pix2real(params, pixCoord):
    # take the pixel coordinates of a point, convert it to real coordinates
    if params["direction"] and \
        params["origin"] and \
        params["parity"]:

        if params["direction"][0] == 0:
            x_r = params["direction"][2] * \
                  (pixCoord.x() - params["origin"].x()) * params["parity"]
        else:
            x_r = params["direction"][2] * \
                  (pixCoord.y() - params["origin"].y()) * params["parity"]

        if params["direction"][1] == 1:
            y_r = params["direction"][2] * \
                  (pixCoord.y() - params["origin"].y()) * params["parity"]
        else:
            y_r = params["direction"][2] * \
                  (pixCoord.x() - params["origin"].x()) * params["parity"]

        return x_r, y_r
    else:
        return False, False

class btImageScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent):
        QtWidgets.QGraphicsScene.__init__(self)
        self.circleRadius = 4
        self.desiredWidth = 640
        self.parent = parent

        self.pixMap = None
        self.frame = None

        self.addItemHolders()
        self.imageFile = None

    def addItemHolders(self):
        # item holders
        self.tempEllipse = None
        self.visualMeasure = [None, None]
        self.visualOrigin = None
        self.positiveVisuals = [ None, None, None ]
        self.visualMeasureLine = None
        self.visualMeasureLineText = None
        self.paramVisuals = [None, None, None, None]
        self.limitVisuals = [None, None]
        self.fingerprintVisuals = []

        self.beaconVisuals = []
        self.dongleVisuals = []

    def addPixItem(self, item):
        self.pixItem = item
        self.addItem(item)

    def setImageSize(self, size):
        self.sizeX = size.width()
        self.sizeY = size.height()

    def removeVisualMeasureLine(self):
        if self.visualMeasureLine:
            self.removeItem(self.visualMeasureLine)

        self.visualMeasureLine = None
        self.visualMeasureLineText = None

    def addMeasureLine(self, p1, p2):
        self.removeVisualMeasureLine()

        self.visualMeasureLine = self.addLine(p1.x(), p1.y(), p2.x(), p2.y(),
                     QtGui.QPen(QtGui.QColor(255,0,0)))

        # put distance info
        if self.parent.params["parity"]:
            norm = math.sqrt(
                (p1.x() - p2.x()) ** 2 + \
                (p1.y() - p2.y()) ** 2) * \
               self.parent.params["parity"]
            unit = "m"
        else:
            norm = math.sqrt(
                (p1.x() - p2.x()) ** 2 + \
                (p1.y() - p2.y()) ** 2)
            unit = "px"

        self.visualMeasureLineText = QtWidgets.QGraphicsSimpleTextItem(
                "%s %s" % (round(norm, 2), unit))

        self.visualMeasureLineText.setPos(
            (p1.x() + p2.x()) / 2 - 15, (p1.y() + p2.y()) / 2)

        self.visualMeasureLineText.setFont(QtGui.QFont('Mono', 5))
        self.visualMeasureLineText.setParentItem(self.visualMeasureLine)

    def addPoint(self, point, text = "", color = QtGui.QColor(0, 0, 0),
                 radius = None, penColor = None, penWeight = None,
                 eventTrigger = False ):
        if not radius:
            radius = self.circleRadius
        color = QtGui.QColor(color)
        xoffset = 20
        yoffset = 8
        pn = QtGui.QPen()

        if penWeight:
            pn.setWidth(penWeight)

        if penColor:
            pn.setColor(penColor)
        else:
            pn.setColor(color)

        br = QtGui.QBrush()
        br.setStyle(1) # RadialGradient pattern
        br.setColor(color)
        brText = QtGui.QBrush()
        brText.setStyle(1) # RadialGradient pattern
        brText.setColor(QtGui.QColor(96,96,96))
        if eventTrigger:
            newEllipse = btEllipseItem(
                point.x() - radius,
                point.y() - radius,
                2 * radius,
                2 * radius,
                parent=self
            )
        else:
            newEllipse = QtWidgets.QGraphicsEllipseItem(
                            point.x() - radius,
                            point.y() - radius,
                            2 * radius,
                            2 * radius)
        newEllipse.setBrush(br)
        newEllipse.setPen(pn)
        if point.x() > radius \
                and point.y() > radius \
                and point.x() < self.sizeX - radius \
                and point.y() < self.sizeY - radius:
        
        
            if point.x() < xoffset:
                text_x = xoffset
            elif point.x() > self.sizeX - xoffset:
                text_x = self.sizeX - 2 * xoffset
            else:
                text_x = point.x() - xoffset
        
            if point.y() < yoffset:
                text_y = 2 * yoffset
            elif point.y() > self.sizeY - yoffset:
                text_y = self.sizeY - 2 * yoffset
            else:
                text_y = point.y() - 2 * yoffset
        
            if len(text) > 5:
                newText = QtWidgets.QGraphicsSimpleTextItem(text)
                newText.setPos(
                    text_x,
                    text_y
                )
            else:
                newText = QtWidgets.QGraphicsSimpleTextItem(text)
                newText.setPos(
                    text_x + xoffset - 5,
                    text_y
                )
        
            newText.setFont(QtGui.QFont('Mono',5))
            newText.setParentItem(newEllipse)
        
            newText.setBrush(brText)
        self.addItem(newEllipse)
        return newEllipse

    def printAllVisuals(self):
        print("BeaconVisuals")
        for beacon in self.beaconVisuals:
            print(beacon)

        print("DonglesVisuals")
        for dongle in self.dongleVisuals:
            print(dongle)

        print("Positive Visuals")
        for positive in self.positiveVisuals:
            print(positive)

        print("Fingerprint Visuals")
        for fingerprint in self.fingerprintVisuals:
            print(fingerprint)

        print("Limit Visuals")
        for limit in self.limitVisuals:
            print(limit)

        print("Param Visuals")
        for param in self.paramVisuals:
            print(param)

    # def removePositiveVisuals(self):
    #     if any(self.positiveVisuals):
    #         self.removeItem(self.positiveVisuals[0])
    #         self.removeItem(self.positiveVisuals[1])
    #         self.removeItem(self.positiveVisuals[2])
    #
    #     self.positiveVisuals = [None, None, None]

    def addPositiveVisuals(self):

        if self.parent.params["origin"] and self.parent.params["direction"]:
            arrPoint = QtCore.QPoint(self.parent.params["origin"].x() +
                                     self.parent.params["direction"][2] * 30,
                                     self.parent.params["origin"].y() +
                                     self.parent.params["direction"][3] * 30)

            arrow1, arrow2 = self.getArrowHead(
                self.parent.params["origin"],arrPoint)
            self.positiveVisuals[0] = self.addLine(
                self.parent.params["origin"].x(),
                self.parent.params["origin"].y(),
                arrPoint.x(),
                arrPoint.y(),
                QtGui.QPen(QtGui.QColor(0, 255, 0)))

            self.positiveVisuals[1] = self.addLine(
                arrPoint.x(),
                arrPoint.y(),
                arrow1[0],
                arrow1[1],
                QtGui.QPen(QtGui.QColor(0, 255, 0))
            )

            self.positiveVisuals[2] = self.addLine(
                arrPoint.x(),
                arrPoint.y(),
                arrow2[0],
                arrow2[1],
                QtGui.QPen(QtGui.QColor(0, 255, 0))
            )

    def removeDeviceVisuals(self):
        for item in self.beaconVisuals:
            self.removeItem(item)
        for item in self.dongleVisuals:
            self.removeItem(item)
        self.beaconVisuals.clear()
        self.dongleVisuals.clear()

    def addDeviceVisuals(self):
        for beacon in self.parent.beacons:
            if self.parent.beacons[beacon][0]:
                if self.parent.beacons[beacon][1]:
                    item = self.addPoint(
                        real2pix(self.parent.params,
                                 self.parent.beacons[beacon][0]),
                        text=beacon[12:],
                        color=self.parent.beacons[beacon][1])
                else:
                    item = self.addPoint(
                        real2pix(self.parent.params,
                                 self.parent.beacons[beacon][0]))
                item.setData(QtCore.Qt.UserRole, beacon)
                self.beaconVisuals.append(item)

        for dongle in self.parent.dongles:
            if self.parent.dongles[dongle][0]:
                if self.parent.dongles[dongle][1]:
                    item = self.addPoint(
                        real2pix(self.parent.params,
                                 self.parent.dongles[dongle][0]),
                        color=self.parent.dongles[dongle][1],
                        penColor = QtGui.QColor(0, 0, 100),
                        penWeight = 2)
                else:
                    item = self.addPoint(
                        real2pix(self.parent.params,
                                 self.parent.dongles[dongle][0]),
                        penColor = QtGui.QColor(0,0,0),
                        penWeight = 2)
                item.setData(QtCore.Qt.UserRole, dongle)
                self.dongleVisuals.append(item)

    def removeFingerprintVisuals(self):
        for item in self.fingerprintVisuals:
            self.removeItem(item)
        self.fingerprintVisuals.clear()

    def addFingerprintVisuals(self):
        for each in self.parent.data:
            if each in self.parent.listPointItems.keys():
                if self.parent.listPointItems[each].isSelected():
                    item = self.addPoint(real2pix(self.parent.params, each),
                                            str(each[0])+", "+str(each[1]),
                                            QtGui.QColor(0,0,0,120),
                                            penColor=QtGui.QColor(0,0,0),
                                            penWeight=2
                    )
                else:
                    item = self.addPoint(real2pix(self.parent.params, each),
                                            str(each[0])+","+str(each[1]),
                                            QtGui.QColor(255,255,255,0),
                                            penColor=QtGui.QColor(0,0,0)
                                            )

                self.fingerprintVisuals.append(item)

    def addVisuals(self):
        if not self.pixMap:
            return
        self.addParamVisuals()
        self.addPositiveVisuals()
        self.addFingerprintVisuals()
        self.addDeviceVisuals()

    def removeVisuals(self):
        self.removeVisualMeasureLine()
        for item in self.items():
            self.removeItem(item)

        self.addItemHolders()

    def addParamVisuals(self):
        if not self.parent.params["limits"]:
            return

        p0 = real2pix(self.parent.params, self.parent.params["limits"][0])
        p1 = real2pix(self.parent.params, self.parent.params["limits"][1])
        # self.limitVisuals[0] = self.addPoint(
        #     p0, "%s,%s" % ( round(p0.x(), 2), round(p0.y(), 2)),
        #         QtGui.QColor(128, 0, 128))
        # self.limitVisuals[1] = self.addPoint(
        #     p1, "%s,%s" % ( round(p1.x(), 2), round(p1.y(), 2)),
        #         QtGui.QColor(128, 0, 128))
        self.paramVisuals[0] = self.addLine(p0.x(), p0.y(), p0.x(), p1.y(),
                                     QtGui.QPen(QtGui.QColor(255, 0, 255)))
        self.paramVisuals[1] = self.addLine(p0.x(), p0.y(), p1.x(), p0.y(),
                                     QtGui.QPen(QtGui.QColor(255, 0, 255)))
        self.paramVisuals[2] = self.addLine(p0.x(), p1.y(), p1.x(), p1.y(),
                                     QtGui.QPen(QtGui.QColor(255, 0, 255)))
        self.paramVisuals[3] = self.addLine(p1.x(), p0.y(), p1.x(), p1.y(),
                                     QtGui.QPen(QtGui.QColor(255, 0, 255)))

    def getArrowHead(self, s, d, headsize=8):
        dx, dy = s.x() - d.x(), s.y() - d.y()
        norm = math.sqrt(dx ** 2 + dy ** 2)
        udx, udy = dx / norm, dy / norm
        ax = udx * math.sqrt(3) / 2 - udy * 1 / 2
        ay = udx * 1 / 2 + udy * math.sqrt(3) / 2
        bx = udx * math.sqrt(3) / 2 + udy * 1 / 2
        by = - udx * 1 / 2 + udy * math.sqrt(3) / 2

        return (d.x() + headsize * ax, d.y() + headsize * ay), \
               (d.x() + headsize * bx, d.y() + headsize * by)

    def addArrow(self, s, d, color = QtGui.QColor(0, 255, 0), weight = None):

        pen = QtGui.QPen(color)
        if not weight == None:
            pen.setWidth(weight)

        arrow = [None, None, None]

        if not s == d:
            # norm 0 olmasin diye koyduk bu if'i
            arrow1, arrow2 = self.getArrowHead(s, d)
            arrow[0] = self.addLine(
                s.x(),
                s.y(),
                d.x(),
                d.y(),
                pen
            )

            arrow[1] = self.addLine(
                d.x(),
                d.y(),
                arrow1[0],
                arrow1[1],
                pen
            )

            arrow[2] = self.addLine(
                d.x(),
                d.y(),
                arrow2[0],
                arrow2[1],
                pen
            )
        return arrow

    def saveImage(self, imageFile):
        self.setSceneRect(self.itemsBoundingRect())

        img = Qt.QImage(self.sceneRect().size().toSize(),
                        Qt.QImage.Format_ARGB32)
        img.fill(QtCore.Qt.transparent)
        ptr = Qt.QPainter(img)
        self.render(ptr)
        img.save(imageFile)
        ptr.end()

    def updateImage(self, imageFile, imageTrigger = True):
        # self.printAllVisuals()
        self.removeVisuals()
        self.clear()

        if not imageFile:
            return

        if not self.frame or not imageFile == self.imageFile:
            self.frame = QtGui.QImage(imageFile)
            # check image size and save if necessary
            if self.frame.width() > self.desiredWidth:
                if not self.imagePopup(imageFile):
                    self.log("Image too large!")
                    return

            self.frame = self.setOpacity(.25)
            self.log("Image loaded: %s." % (imageFile))
            self.imageFile = imageFile

        self.pixMap = btPixmap().fromImage(self.frame)
        if imageTrigger:
            self.pixItem = btPixmapItem(self)
        else:
            self.pixItem = QtWidgets.QGraphicsPixmapItem()
        self.pixItem.setPixmap(self.pixMap)
        self.addPixItem(self.pixItem)

        self.setImageSize(self.frame.size())
        self.update()
        self.addVisuals()

    def setOpacity(self, opacity):
        newImage = QtGui.QImage(self.frame.size(), QtGui.QImage.Format_ARGB32)
        newImage.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter (newImage)
        painter.setOpacity(opacity)
        painter.drawImage(
                QtCore.QRect(0, 0,
                            self.frame.width(),
                            self.frame.height()),self.frame)

        return newImage

    def imagePopup(self, imageFile):
        choice = QtWidgets.QMessageBox.question(self.parent, 'Resize Image',
                                            "Image width is higher than "
                                            "expected. Should I shrink and "
                                            "save it?",
                                            QtWidgets.QMessageBox.Yes |
                                            QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            fileName = os.path.basename(imageFile)
            self.frame = self.frame.scaledToWidth(self.desiredWidth)
            imageFile = os.path.join(pathMap, fileName)
            self.frame.save(imageFile)
            self.log("Saving file to: %s." % (imageFile))
            return True
        else:
            return False

    def log(self, msg):
        # print(msg)
        self.parent.log(msg)

class btPixmap(QtGui.QPixmap):
    def __init__(self):
        super(btPixmap, self).__init__()

class btPixmapItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent):
        super(btPixmapItem, self).__init__()
        self.parent = parent

    def mousePressEvent(self,event):
        # QGraphicsScene cannot receive the points properly,
        # thus QGraphicsPixmapItem hands them over
        self.parent.pointOverride(event.pos(), data = None)


class btEllipseItem(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, parent):
        super(btEllipseItem, self).__init__(x,y,w,h)
        self.parent = parent
        self.x = x
        self.w = w
        self.y = y
        self.h = h

    def mousePressEvent(self, event):
        self.parent.pointOverride(event.pos(), data = self.data(QtCore.Qt.UserRole))
        newRadius = 15
        self.changeSize(newRadius)

    def changeSize(self, newRadius):
        self.x = self.x + int(self.w/2) - newRadius
        self.y = self.y + int(self.h/2) - newRadius
        self.w = newRadius * 2
        self.h = newRadius * 2
        self.setRect(self.x,
                     self.y,
                     self.w,
                     self.h)


class btPopup(QtWidgets.QWidget):
    def __init__(self, name):
        super().__init__()

        self.name = name

        self.initUI()

    def initUI(self):
        lblName = QtWidgets.QLabel(self.name, self)
