import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import Delaunay
import json
import scipy
import argparse
import sys
import math
import numpy as np

sys.path.append('./bin')
import HJSON
import HCOMMON

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bens Algorithm for SoCG')
    parser.add_argument('file')
    parser.add_argument('-s', type=int, nargs='?', default=100, dest='sky', help='Only the sky is the limit.')
    parser.add_argument('-p', type=int, nargs='?', default=0, dest='plot', help='Plot it, if you must')
    parser.add_argument('-v', action='store_true', dest='verbose', help='Print debug messages, if you must')
    arguments = parser.parse_args()

    start_t = HCOMMON.snaptime()
# =============================================================================
# setup -----------------------------------------------------------------------
    instance_points,instance = HJSON.readTestInstance(arguments.file)

    if arguments.plot:
        fig = plt.figure()
        if arguments.plot == 1:
            ax = fig.add_subplot(111, projection='3d')
            for p in instance_points:
                ax.scatter(p[0], p[1], c="b", marker='o', s=len(instance_points))
        if arguments.plot == 2:
            ax = fig.add_subplot(111)
            for p in instance_points:
                ax.plot(p[0], p[1], c="b", marker='o')

# =============================================================================
# triangulation of instance points  -------------------------------------------
    t_tri = Delaunay(instance_points)

    t_edges = []
    for sim in t_tri.simplices: # append all inner edges to t_edges
        for i in range(len(sim)-1):
            t_edges.append([sim[i-1], sim[i]])
    for ch in t_tri.convex_hull: # append convex hull to t_edges
        ap = True
        for e in t_edges:
            if (ch[0] == e[0] and ch[1] == e[1]) or (ch[0] == e[1] and ch[1] == e[0]):
                ap = False
        if ap:
            t_edges.append([ch[0],ch[1]])
    HCOMMON.snapshoot(start_t, "triangulation1", arguments.verbose)
    start_t = HCOMMON.snaptime()
# =============================================================================
# calculate and draw start points   -------------------------------------------
    start_points=[]
    for e in t_edges:
        """plt.plot((instance_points[e[0]][0], instance_points[e[1]][0]),
                (instance_points[e[0]][1], instance_points[e[1]][1]), "b--")"""
        X1 = instance_points[e[0]][0]
        X2 = instance_points[e[1]][0]
        Y1 = instance_points[e[0]][1]
        Y2 = instance_points[e[1]][1]
        start_points.append([
            (X1 + X2) / 2,
            (Y1 + Y2) / 2,
            scipy.linalg.norm([X1-X2,Y1-Y2]),
            0 # outgoing s_edges count
            ])

    HCOMMON.snapshoot(start_t, "startpoints", arguments.verbose)
    start_t = HCOMMON.snaptime()
# =============================================================================
# calculate triangulation of starting point graph   ---------------------------
    start_points_td = []
    for s in start_points:
        start_points_td.append([s[0],s[1]])
    s_tri = Delaunay(start_points_td)

    HCOMMON.snapshoot(start_t, "triangulation2", arguments.verbose)
    start_t = HCOMMON.snaptime()

    s_edges = []
    for sim in s_tri.simplices: # append all inner edges to t_edges
        for i in range(len(sim)-1):
            s_edges.append([sim[i-1], sim[i]])

    HCOMMON.snapshoot(start_t, "+simplices", arguments.verbose)
    start_t = HCOMMON.snaptime()
    """ TODO we decided not to use this, cause it took forever
    for ch in s_tri.convex_hull: # append convex hull to t_edges
        ap = True
        for e in s_edges:
            if (ch[0] == e[0] and ch[1] == e[1]) or (ch[0] == e[1] and ch[1] == e[0]):
                ap = False
        if ap:
            s_edges.append([ch[0],ch[1]])

    HCOMMON.snapshoot(start_t, "+convex hull", True)
    start_t = HCOMMON.snaptime()
    """
# =============================================================================
# calculate metrics for outgoing edges  ---------------------------------------
    for e in s_edges: # save point with higher z value in first place
        if start_points[e[0]][2] < start_points[e[1]][2]:
            e[0],e[1] = e[1],e[0]
    for e in s_edges: # sum outgoing edges for each starting point
        start_points[e[0]][3] += 1

    start_points.sort(key=lambda x: x[3], reverse=True)

    mi, avg, ma, lim = start_points[0][3], 0, 0, start_points[math.floor(len(start_points)/10)*9][3]
    for s in start_points:
        if mi > s[3]: mi = s[3]
        avg += s[3]
        if ma < s[3]: ma = s[3]
    avg /= len(start_points)

    def f(x,y):
        return np.sin(np.sqrt(x ** 2 + y ** 2))

    HCOMMON.snapshoot(start_t, "metrics", arguments.verbose)
    start_t = HCOMMON.snaptime()
# =============================================================================
# plot starting point graph ---------------------------------------------------
    out = []
    x,y,z,w = [],[],[],[]
    for i,s in enumerate(start_points):
        x.append(s[0])
        y.append(s[1])
        z.append(s[2])
        if (s[3] > max(avg,lim)) and (i < arguments.sky) and (i < (len(instance_points)/3)):
            out.append([s[0],s[1]])
            w.append((s[3]*1000)*-1)
        else:
            w.append(0)

    if arguments.verbose: print("#%d, limit: %d, avg: %d" % (len(out), lim, avg))

    if arguments.plot == 1:
        for e in s_edges: # starting point graph edges
            plt.plot((start_points[e[0]][0], start_points[e[1]][0]),
                    (start_points[e[0]][1], start_points[e[1]][1]),
                    (start_points[e[0]][2], start_points[e[1]][2]),
                    "g-")

        for i,s in enumerate(start_points): # plot altitude of starting points
            plt.plot((s[0], s[0]), (s[1], s[1]), (w[i], s[2]), "r:")

        for p in start_points: # color starting points based on metric
            color = "b"
            if p[3] == mi:
                color="g"
            if p[3] == ma:
                color="r"
            ax.scatter(p[0], p[1], p[2], c=color, marker="o")

        ax.plot_trisurf(x, y, z, cmap='prism', edgecolor='none');
        ax.plot_trisurf(x, y, w, cmap='Set1', edgecolor='none');
    if arguments.plot == 2:
        for o in out:
            plt.plot(o[0], o[1], "r.")

    if arguments.plot:
        plt.show()

    HCOMMON.snapshoot(start_t, "limit", arguments.verbose)


# =============================================================================
# write to json file ----------------------------------------------------------
filename = arguments.file
filename = "startpoints/" + filename.split("/",1)[-1] # fix path
filename = filename.split(".",1)[0] + ".sky-" + str(min(arguments.sky, math.floor(len(instance_points)/3))) +".json" # substitute "instance" with "solution"

data = {
        "type": "Startpoints",
        'instance_name' : instance,
        "points": []
    }
for o in out:
    data['points'].append({'x': o[0], 'y': o[1]})

with open(filename, 'w') as json_file:
            json.dump(data, json_file)
