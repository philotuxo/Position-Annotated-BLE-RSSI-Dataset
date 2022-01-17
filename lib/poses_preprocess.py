import numpy as np

def updateLists(listShow, listPos, listPosinC, listIds, listArr, listOri) :
    indices = [i for i in range(len(listShow)) if listShow[i] == 1]
    listShow = [listShow[i] for i in indices]
    listPosinC = [listPosinC[i] for i in indices]
    listPos = [listPos[i] for i in indices]
    listOri = [listOri[i] for i in indices]
    listArr = [listArr[i] for i in indices]
    listIds = [listIds[i] for i in indices]

    return listShow, listPos, listPosinC, listIds, listArr, listOri


def axisBasedElimination(listShow, listCenterPx, frameCenter, selection = 10):
    N = len(listCenterPx)
    M = sum(listShow)

    indices = [0] * M
    weights = [0.0] * M

    counter = 0
    for i in range(N):
        if listShow[i] == 1:
            indices[counter] = i
            weights[counter] = np.linalg.norm(listCenterPx[i] - frameCenter)
            counter += 1

    orders = np.argsort(weights)

    for i in range(len(orders)):
        if i >= selection:
            listShow[indices[orders[i]]] = 0
    return listShow

def selectClosest(listShow, listPosinC, selection = 1):

    N = len(listPosinC)
    M = sum(listShow)
    indices = [0] * M
    weights = [0.0] * M

    counter = 0
    for i in range(N):
        if listShow[i] == 1:
            indices[counter] = i
            weights[counter] = np.linalg.norm(listPosinC[i])
            counter += 1

    orders = np.argsort(weights)


    for i in range(len(orders)):
        if i >= selection:
            listShow[indices[orders[i]]] = 0
    return listShow


def outlierFilter(listShow, listPos, selection = 1):

    N = len(listPos)

    while sum(listShow) > selection:
        # get the cluster center
        S = np.array([0.0,0.0,0.0])
        counter = 0
        for i in range(N):
            if listShow[i] == 1:
                counter += 1
                S += listPos[i]
        m = S/counter

        # find the index with maximum residual
        mx = 0
        imx = None
        for i in range(N):
            if listShow[i] == 1:
                res = np.linalg.norm(m - listPos[i])
                # print(res,i,imx,m, listPos[i])
                if res >= mx:
                    mx = res
                    imx = i
        if not imx == None:
            listShow[imx] = 0
    return listShow

def distanceFilter(listShow, listPosinC, threshold = 10.0):
    weights = []

    for i in range(len(weights)):
        weights[i] = np.linalg.norm(listPosinC[i])
        if weights[i] > threshold:
            listShow[i] = 0

    return listShow

def getMarkerCenterPixel(markerCorners):
    return np.mean(markerCorners,axis=0)