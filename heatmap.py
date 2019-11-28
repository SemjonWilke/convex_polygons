import matplotlib.pyplot as plt
import argparse
import json
import sys
import scipy
from scipy.spatial import distance

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('-n', '--num', type=int, default=10, nargs=1, dest='num')
    parser.add_argument('-s', '--sense', type=int, default=12, nargs=1, dest='sense')
    arguments = parser.parse_args()
    readInstance(arguments.file)
    for p in points:
        plt.plot(p[0], p[1], "b.")
    map(arguments.num[0], arguments.sense)
    plt.show()
    