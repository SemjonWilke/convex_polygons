import matplotlib.pyplot as plt
import argparse
import json
import sys
import scipy
import math
import random
from scipy.spatial import distance
from sklearn.cluster import KMeans

import HCOMMON

points = []

def readInstance(filename):
    global points
    with open(filename) as json_file:
        data = json.load(json_file)
        for p in data['points']:
            points.append([int(p['x']), int(p['y'])])
        json_file.close()

def map(num, sense):
    xstart = min([p[0] for p in points])
    xend = max([p[0] for p in points])
    ystart = min([p[1] for p in points])
    yend = max([p[1] for p in points])
    xspan = xend - xstart
    yspan = yend - ystart
    xstart += xspan * 0.05
    ystart += yspan * 0.05
    xfactor = int((xspan * 0.9) / (num-1))
    yfactor = int((yspan * 0.9) / (num-1))

    m = scipy.array([[[(0,0),0,0,0]]*num]*num)
    s = 0
    t = (num**2 * len(points)) / 100
    for i,k in enumerate(m):
        for j,l in enumerate(k):
            for p in points:
                s += 1
                print("\ri = %0.0f%%" % (s / t), end = '')
                sys.stdout.flush()
                v = (round(xstart + (i*xfactor)), round(ystart + (j*yfactor)))
                d = distance.euclidean(p, v)
                m[i][j][0] = v
                if m[i][j][1] == 0 or d < m[i][j][1]:
                    m[i][j][1] = d #min distance to any point
                m[i][j][2] += d #avg distance to all points
            m[i][j][2] /= int(round(len(points))) #scale avg
            ex = (m[i][j][1]/m[i][j][2])*100
            if ex > sense:
                #print("min[%d]/avg[%d] = %4.1f%%" % (m[i][j][1], m[i][j][2], ex))
                plt.plot(v[0], v[1], "rP")

def findClusterCenters(points, retr=12, plot=False, verbose=False):
    kmeans = None
    kcol = []
    start_t = HCOMMON.snaptime()

    if verbose: print("find clusters with kmeans")
    wcss = []
    ceiling = min(100, round(len(points)/2))
    for k in range(0, ceiling):
        prev = kmeans
        kmeans = KMeans(n_clusters=k+1, n_init=retr, n_jobs=4, random_state=0).fit(points)
        if k == 0:
            wcstart = kmeans.inertia_
        wcss.append(kmeans.inertia_ / wcstart)
        if k > 0 and plot:
            if verbose: print("\rkmeans k = %d of %d" % (k, ceiling), end='')
            wp = (wcss[k] - wcss[k-1], k - (k-1)) # vektor verschieben nach 0,0
            phi = math.degrees(math.atan(wp[0]/wp[1]))
            for c in kmeans.cluster_centers_: #TODO: send colors and plot to HVIS
                col = hex(random.randint(10,16777215)).split('x')[1]
                while len(col) < 6:
                    col = '0'+col
                col ='#'+col
                kcol.append(col)
                #axs[1].plot([k,k-1], [wcss[k],wcss[k-1]], color=col, linestyle='-') TODO plot in HVIS only
            if wcss[k] < 0.10:
                kmeans = prev
                if verbose: print("")
                return
    HCOMMON.snapshoot(start_t, 'clustering', verbose) #TODO import HCOMMON
