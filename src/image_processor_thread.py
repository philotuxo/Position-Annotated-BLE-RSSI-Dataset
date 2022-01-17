import sys
sys.path.append("..")
from lib.arCommon import *
import time
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread
from lib.poses_preprocess import *

def rot2d(theta):
    return np.matrix([[np.cos(theta),  -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])

class ImageProcessorThread(QThread):

    def __init__(self, name, grabQ, inQ, guiQ, imQ, markers, kalmanPars):
        QThread.__init__(self)
        self.name = name
        self.grabQ = grabQ
        self.inQ = inQ
        self.guiQ = guiQ
        self.imQ = imQ
        self.markers = markers
        self.sendImg = True
        self.waiting = False
        self.skipped = 0
        self.flushOn = False
        self.pars = kalmanPars
        self.distCoeffs = ()
        self.cameraMatrix = ()
        
        self.rotListMarker2World = {}
        self.getRotMarker2Camera()


    def getRotMarker2Camera(self):
        for i in self.markers.keys():
            # Rot, Jacob = cv2.Rodrigues(
            #     np.matrix(self.markers[i][1]))
            self.rotListMarker2World[i] = invRotMat(self.markers[i][1])
        # print(self.markers[0][1])
        # print(self.rotListMarker2World[0])
        # print(invRotMat(self.markers[0][1]))



    def setMatrices(self):
        # transition error (process noise covariance)
        Q = np.matrix(np.diag([self.pars[0],
                               self.pars[0],
                               self.pars[0],
                               self.pars[1],
                               self.pars[1],
                               self.pars[1],
                               self.pars[1],
                               self.pars[1],
                               self.pars[1],
                               self.pars[1],
                               self.pars[1],
                               self.pars[1]]))
        # observation error (sensor noise covariance)
        R = np.matrix(np.diag([self.pars[2],
                               self.pars[2],
                               self.pars[2],
                               self.pars[3],
                               self.pars[3],
                               self.pars[3],
                               self.pars[3],
                               self.pars[3],
                               self.pars[3],
                               self.pars[3],
                               self.pars[3],
                               self.pars[3]]))

        return (Q, R)


    def flushOver(self, queueSizeTH=5):
        while self.imQ[0].qsize() > queueSizeTH:
            self.skipped += 1
            dummy = self.imQ[0].get()

        while self.imQ[1].qsize() > queueSizeTH:
            self.skipped += 1
            dummy = self.imQ[1].get()

    def run(self):
        dictionary = cv2.aruco.getPredefinedDictionary(arucoDict)


        # kalman filter parameters
        A = np.matrix(np.diag([1,1,1,1,1,1,1,1,1,1,1,1])) # dimensions are independent
        H = np.matrix(np.diag([1,1,1,1,1,1,1,1,1,1,1,1])) # observation dimensions are
        # independent
        P = np.matrix(np.ones(shape=[12,12])) # error covariance initial value

        Q,R = self.setMatrices()

        X = None
        arrowEnd = None
        process = False
        ending = [False, False]
        # if first run
        first = True
        paused = False
        kalman = True
        reverseFacing = None
        frameCount0 = 0
        frameCount1 = 0
        batch_size = 1
        tstamp = 0.0

        self.guiQ.put(['S', self.name])

        listPos = []
        listPosinC = []
        listOri = []
        listArr = []
        listIds = []
        listShow = []
        listCenterPx = []

        process_counter = 0

        while True:
            # inQueue parser
            if self.inQ.qsize() > 0:
                # flush inQueue
                incoming = self.inQ.get()
                msg = incoming[0]
                if msg == 'P':
                    if paused:
                        paused = False
                    else:
                        paused = True
                if msg == 'T':
                    self.sendImg = True
                if msg == 'F':
                    self.sendImg = False
                if msg == 'K':
                    kalman = True
                if msg == 'M':
                    kalman = False
                if msg == 'A':
                    self.pars = incoming[1]
                    # print(self.pars)
                    Q, R = self.setMatrices()
                if msg == 'O':
                    reverseFacing = incoming[1]
                if msg == 'L':
                    self.flushOn = True
                if msg == 'H':
                    self.flushOn = False
                if msg == 'C':
                    key = incoming[1]
                    self.cameraMatrix = np.array(camParameters[key][0])
                    self.distCoeffs = np.array(camParameters[key][1])
                if msg == 'B':
                    batch_size = incoming[1]
                if msg == 'TS':
                    self.guiQ.put(['TS', tstamp])
                if msg == 'E':
                    ending[incoming[1]] = True

            if self.imQ[0].qsize() == 0 and self.imQ[1].qsize() == 0:
                process = False
                if all(ending):
                    self.guiQ.put(['Q'])

            if self.imQ[0].qsize() > 0 and self.imQ[1].qsize() > 0:
                # iki kameradan birden geliyorsa
                if frameCount0 <= frameCount1:
                    camNo, frameCount0, tstamp, frame = self.imQ[0].get()
                    process = True
                    process_counter += 1
                    frameCount = frameCount0
                else:
                    camNo, frameCount1, tstamp, frame = self.imQ[1].get()
                    process = True
                    process_counter += 1
                    frameCount = frameCount1
            else:
                if self.imQ[0].qsize() > 0:
                    camNo, frameCount0, tstamp, frame = self.imQ[0].get()
                    process = True
                    process_counter += 1
                    frameCount = frameCount0
                if self.imQ[1].qsize() > 0:
                    camNo, frameCount1, tstamp, frame = self.imQ[1].get()
                    process = True
                    process_counter += 1
                    frameCount = frameCount1

            if self.flushOn == True:
                self.flushOver()

            if paused or self.waiting:
                time.sleep(time_wait)
                continue

            if not process:
                time.sleep(time_wait)
                continue

            height, width, bytesPerLine = frame.data.shape
            frameCenter = np.array([width/2, height/2])
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            markerCorners, markerIds, rejectedCorners = \
                cv2.aruco.detectMarkers(gray, dictionary)

            cv2.aruco.drawDetectedMarkers(frame, markerCorners, ids=markerIds,
                                          borderColor=(255, 255, 255))
            if len(markerCorners) > 0:
                if not (markerCorners is not None and markerIds is not None):
                    continue

                for index in range(len(markerCorners)):
                    # check if marker ID is defined in the configuration
                    id = markerIds[index][0]
                    if id not in self.markers.keys():
                        continue

                    corners = markerCorners[index]

                    # rvec: rotation of the marker in the camera frame
                    # tvec: translation of the marker in the camera frame
                    rvec, tvec, objPoints = cv2.aruco.estimatePoseSingleMarkers(
                        corners, markerSize,
                        self.cameraMatrix, self.distCoeffs)

                    pos_marker_in_camera = np.matrix(tvec[0][0]).T

                    pos_marker_in_world = np.matrix(self.markers[id][0]).T

                    rot_marker_to_world = rotMat(self.markers[id][1])
                    # rotation for camera coords w.r.t. marker frame
                    rot_marker_to_camera, Jacob = cv2.Rodrigues(
                        np.matrix(rvec[0][0]))

                    # final rotation matrix from world coordinates to camera,
                    # we are multiplying from the reverse
                    rot_camera_to_world = rot_marker_to_world *  \
                                      rot_marker_to_camera.T

                    # translate to world coords
                    pos_camera_in_world = pos_marker_in_world - \
                                      rot_camera_to_world * pos_marker_in_camera

                    # again multiplying from the reverse

                    # print(repr(np.array(pos_camera_in_world)), repr(id),
                    #            repr(np.array(pos_marker_in_camera)))


                    listCenterPx.append(getMarkerCenterPixel(corners[0]))
                    listPos.append(pos_camera_in_world.T.tolist()[0])
                    listPosinC.append(pos_marker_in_camera.T.tolist()[0])

                    if reverseFacing == camNo:
                        # add an offset rotation for the reverse camera

                        ori3D = (rotZ(np.pi) * rot_camera_to_world).reshape(9)

                        arrowEnd = pos_marker_in_world \
                            - (rot_camera_to_world * pos_marker_in_camera) \
                            + (rotZ(np.pi) * rot_camera_to_world * np.matrix([
                            0,0,.5]).T)

                    else:
                        # orientation line end coordinates
                        ori3D = rot_camera_to_world.reshape(9)

                        arrowEnd = pos_marker_in_world \
                            - (rot_camera_to_world * pos_marker_in_camera) \
                            + (rot_camera_to_world * np.matrix([0,0,.5]).T)

                    # print(ori3D[0].round(4).tolist())


                    listIds.append(id)
                    listArr.append(arrowEnd.T.tolist()[0])
                    listOri.append(ori3D.tolist()[0])

                    if self.sendImg:
                        cv2.aruco.drawAxis(frame,
                                       self.cameraMatrix,
                                       self.distCoeffs,
                                       rvec,
                                       tvec,
                                       markerSize/2)
            if process_counter % batch_size != 0:
                # don't send anything
                continue

            if len(listPos) > 0:
                listShow = [1] * len(listPos)

                # # once en yakin 15 taneyi al
                # # listShow = distanceFilter(listShow, listPosinC, 7.5)
                # listShow = selectClosest(listShow, listPosinC, 15)
                # listShow = selectClosest(listShow, listPosinC, 1)
                # print()
                #print(listShow)
                # print(sum(listShow), len(listShow))

                # print(listShow)

                # listShow = axisBasedElimination(
                #     listShow, listCenterPx, frameCenter, 10)
                # print(listShow)

                # listShow = selectClosest(listShow, listPosinC, 20)
                # listShow = outlierFilter(listShow, listPos, 10)
                # print(listShow)

                #
                #listShow, listPos, listPosinC, listIds, listArr, listOri = updateLists(
                    #listShow, listPos, listPosinC, listIds, listArr, listOri
                #)
                #
                # listShow, listPos, listPosinC, listIds, listArr, listOri = updateLists(
                #     listShow, listPos, listPosinC, listIds, listArr, listOri
                # )
                #
                # # sonra ortalamaya en yakin 3 taneyi al
                # listShow = outlierFilter(listShow, listPos, 5)
                # # listShow = selectClosest(listShow, listPosinC, 10)
                # # print(listShow)
                #
                # listShow, listPos, listPosinC, listIds, listArr, listOri = updateLists(
                #     listShow, listPos, listPosinC, listIds, listArr, listOri
                # )

                # listShow = outlierFilter(listShow, listPos, 6)

                # print(listOri)

            if len(listPos) > 0:
                # send or not
                if kalman:
                    # print(listPos)
                    if len(listPos) >= 2:
                        meanPos = np.mean(listPos, 0)
                        meanOri = np.mean(listOri, 0)
                    else:
                        meanPos = listPos[0]
                        meanOri = listOri[0]

                    Z = np.matrix(np.append(meanPos, meanOri)).transpose()

                    if first:
                        # initialization
                        X = np.copy(Z)
                    else:
                        # kalman filtering
                        # prediction
                        Xpre = A*X

                        Ppre = A*P*np.transpose(A) + Q

                        # update
                        K = Ppre * H * np.linalg.inv(H* Ppre* np.transpose(H) + R)
                        # gain
                        X = Xpre + K * (Z - H*X )
                        P = (np.identity(12) - K * H) * Ppre

                        # calculate the arrow end ????
                        rotEstimation = X[3:].reshape(3,3)

                        arrowEnd = X[0:3] + \
                                   rotEstimation * np.matrix([0, 0, .5]).T

                    if not first:
                        self.guiQ.put([
                            'K', camNo, frameCount, tstamp,
                            [ np.round(X.transpose(),3).tolist()[0],
                              np.round(arrowEnd.transpose(),3).tolist()[0]]
                        ])
                        self.guiQ.put([ 'C', camNo, frameCount, tstamp, [
                            np.round(X[0:2,0:2].transpose(), 3).tolist()[0],
                            np.round(P[0:2, 0:2],3)]])

                    first = False

                else:

                    # Not kalman
                    self.guiQ.put([ 'M', camNo, frameCount, tstamp, [
                        np.round(listIds,5).tolist(),
                        np.round(listPos,5).tolist(),
                        np.round(listOri,5).tolist(),
                        np.round(listArr,5).tolist(),
                        listShow]])
                    # print(listPos)

            if self.sendImg:
                frame = cv2.resize(frame, (320,240))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, bytesPerLine = frame.data.shape
                cameraMap = QPixmap(
                    QImage(frame.data, width, height, bytesPerLine * width,
                                 QImage.Format_RGB888))

                self.guiQ.put([ 'F', camNo, frameCount, tstamp, cameraMap])

            if process_counter % batch_size == 0:
                listPos.clear()
                listOri.clear()
                listArr.clear()
                listIds.clear()
                listPosinC.clear()
                listCenterPx.clear()

