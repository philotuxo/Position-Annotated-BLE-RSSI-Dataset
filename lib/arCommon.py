import pyudev
import numpy as np
import json
import cv2

time_wait = .01

def getCameras():
    cameras = {}

    context = pyudev.Context()
    devPath = "DEVNAME"
    devID = "MINOR"
    devName = "ID_V4L_PRODUCT"


    v4l_subsystem = 'video4linux'

    for device in context.list_devices(subsystem=v4l_subsystem):
        cameras[int(device.get(devID))] = \
            [device.get(devName), device.get(devPath)]

    return cameras

def invRotX(theta):
    return np.matrix([
        [1, 0, 0],
        [0, np.cos(theta), np.sin(theta)],
        [0, -np.sin(theta), np.cos(theta)]
    ])

def invRotY(theta):
    return np.matrix([
        [np.cos(theta), 0, -np.sin(theta)],
        [0, 1, 0],
        [np.sin(theta), 0, np.cos(theta)]
    ])

def invRotZ(theta):
    return np.matrix([
        [np.cos(theta), np.sin(theta), 0],
        [-np.sin(theta), np.cos(theta), 0 ],
        [0, 0, 1 ]
    ])

def invRotMat(rvec):
    retval = invRotX(rvec[0]) * invRotY(rvec[1]) * invRotZ(rvec[2])
    return retval


def rotX(theta):
    return np.matrix([
        [1, 0, 0],
        [0, np.cos(theta), -np.sin(theta)],
        [0, np.sin(theta), np.cos(theta)]
    ])

def rotY(theta):
    return np.matrix([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

def rotZ(theta):
    return np.matrix([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0 ],
        [0, 0, 1 ]
    ])

def rotMat(rvec):
    retval = rotZ(rvec[2]) * rotY(rvec[1]) * rotX(rvec[0])
    return retval



def readMarkerConfiguration(configFile, selection = None):
    # Marker Configuration
    # ID:[3D position]:[3D orientation]
    markers = {}
    with open(configFile, 'r') as f:
        for line in f:
            splitted = line.split(':',3)
            id = int(splitted[0])
            if not selection == None:
                if not id in selection:
                    continue
            # print(id)
            position = json.loads(splitted[1])
            orientation = json.loads(splitted[2])
            markers[id] = [position, orientation]
    return markers

def cameraCoords(tvec, rvec):
    rvecInv, Jacob = cv2.Rodrigues(rvec)
    newCoord = -tvec * rvecInv
    # print(np.round(newCoord,2), np.round(rvec,2))
    return newCoord

markerSize = 0.298

camParameters = {}

camParameters['Hp-laptop'] = [
    [[ 712.87057841,    0.        ,  308.58799038],
    [   0.        ,  713.04059927,  234.18174338],
    [   0.        ,    0.        ,    1.        ]],

    [[  3.56056587e-01,  -3.25680069e+00,  -6.00198019e-04,
         -7.16181392e-04,   7.41530182e+00  ]]
]

camParameters['Logitech'] = [
    [[661.40628805, 0., 379.81040453],
     [0., 660.23413583, 281.39796918],
     [0., 0., 1.]],
    [[0.06213409, -0.21677386, -0.00047493, -0.0016425, 0.16509759]]
]

##### IPHONE X v1 #####
camParameters['Iphone X Rear'] = [ [
    [1.80574681e+03, 0.00000000e+00, 7.65321122e+02],
    [0.00000000e+00, 1.79742413e+03, 5.90523487e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]],
    [[ 0.09986863, 0.28291512, 0.00931904, -0.04914916,-1.00073786]]
    ]

camParameters['Iphone X Rear 27012020'] = [
    [[1.85639731e+03, 0.00000000e+00, 6.63028114e+02],
     [0.00000000e+00, 1.87371364e+03, 8.39392748e+02],
     [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]],
    [[ 0.09522832, -0.16718939, -0.02236966,  0.00179404, -0.15681415]]
    ]


##### IPHONE X v2 #####
# cameraZart = 4.255149948649531
#
# cameraMatrix = np.array([[1.82376126e+03, 0.00000000e+00, 7.17706123e+02],
#        [0.00000000e+00, 1.79303583e+03, 5.99691034e+02],
#        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
#
# distCoeffs = np.array([[ 0.02435192,  0.31958656,  0.00620617, -0.05683575, -0.52864427]])



# samsung A5 rear camera
# cameraMatrix = np. array([
#     [1.52026163e+03, 0., 1.01749543e+03],
#     [0., 1.50460857e+03, 5.37775634e+02],
#     [0., 0., 1.]]
# )
#
# distCoeffs = np.array([[ 1.98031041e-01, -9.03085712e-01,  7.71732639e-04,
#          2.48112356e-03,  1.39210284e+00]])


# http://argus.web.unc.edu/camera-calibration-database/

##### GoPro Hero 4 Linear 1080p 60fps #####
cameraZart =  0.7742092547625634
camParameters['GoPro Linear'] = [
    [[1.05908634e+03, 0.00000000e+00, 9.55446310e+02],
       [0.00000000e+00, 1.06094427e+03, 5.26189929e+02],
       [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]],
    [[-0.12209009,  0.25532824, -0.00158408,  0.00622484, -0.18405952]]
    ]


# cameraMatrix = np.array([
#     [2.78957511e+03, 0.00000000e+00, 7.99133153e+02],
#     [0.00000000e+00, 2.93656610e+03, 7.07980928e+02],
#     [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]
# )
#
# distCoeffs = np.array([[ -0.03579525,   5.71104535,   0.1849745 ,  -0.03471746,
#         -16.04033234]])

##### GoPro Hero 4 FishEye 1080p 30fps #####
# https://www.theeminentcodfish.com/gopro-calibration/
camParameters['GoPro Fisheye'] = [
   [[857.48296979,   0.,               968.06224829],
    [  0.,           876.71824265,     556.37145899],
    [  0.,           0,                1.          ]],
    [[-2.57624020e-01, 8.77086999e-02, -2.56970803e-04, -5.93390389e-04,
      -1.52194091e-02 ]]
    ]

charucoSquareSize = 0.0598
charucoMarkerSize = 0.0299
charucoHeight = 7
charucoWidth = 5

arucoDict = cv2.aruco.DICT_6X6_50