import matplotlib.pyplot as plt
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
# =============================================================================
# setup -----------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Bens Algorithm for SoCG')
    parser.add_argument('file')
    parser.add_argument('-s', type=int, nargs='?', default=100, dest='sky',
                        help='Only the sky is the limit.')
    parser.add_argument('-v', action='store_true', dest='verbose',
                        help='Print debug messages, if you must')
    parser.add_argument('-p', type=int, nargs="?", default=0, dest='plot',
                        help='Plot, if you must')
    arguments = parser.parse_args()

    instance_points,instance = HJSON.readTestInstance(arguments.file)
# =============================================================================
# triangulation of instance points  -------------------------------------------
    start_t = HCOMMON.snaptime()
    t_tri = Delaunay(instance_points)

    t_edges = []
    for sim in t_tri.simplices: # append all simplex edges to t_edges
        for i in range(len(sim)-1):
            t_edges.append([sim[i-1], sim[i]])
    for ch in t_tri.convex_hull: # append convex hull to t_edges
            t_edges.append([ch[0],ch[1]])
    tmp = []
    start_points = []
    for e in t_edges: # remove duplicates from t_edges
        if e[1] > e[0]:
            e = [e[1], e[0]]
        if e not in tmp:
            tmp.append(e)
            # calculate start points
            X1,X2 = instance_points[e[0]][0], instance_points[e[1]][0]
            Y1,Y2 = instance_points[e[0]][1], instance_points[e[1]][1]
            start_points.append([
                    (X1 + X2) / 2, #X Coord in middle of edge
                    (Y1 + Y2) / 2, #Y Coord ^
                    scipy.linalg.norm([X1-X2,Y1-Y2]), #length of the edge X->Y
                    0 # init outgoing s_edges count
            ])

    HCOMMON.snapshoot(start_t, "triangulation blue", arguments.verbose)
# =============================================================================
# calculate triangulation of starting point graph   ---------------------------
    start_t = HCOMMON.snaptime()
    s_tri = Delaunay([s[:2] for s in start_points])
    HCOMMON.snapshoot(start_t, "triangulation red", arguments.verbose)

    start_t = HCOMMON.snaptime()

    tmp.clear()
    s_edges = []
    for sim in s_tri.simplices: # append all simplex edges to s_edges
        for i in range(len(sim)-1):
            s_edges.append([sim[i-1], sim[i]])
    for ch in s_tri.convex_hull: # append convex hull to s_edges
        s_edges.append([ch[0],ch[1]])
    HCOMMON.snapshoot(start_t, "edges", arguments.verbose)
    start_t = HCOMMON.snaptime()

    for i,e in enumerate(s_edges): # remove duplicates from s_edges
        if arguments.verbose: print("\r%.1f%%" % ((i/len(s_edges))*100), end="")
        if e[1] > e[0]:
            e = [e[1], e[0]]
        if e not in tmp:
            # save point with higher z value in first place
            if start_points[e[0]][2] < start_points[e[1]][2]:
                e[0],e[1] = e[1],e[0]
            tmp.append(e)
            start_points[e[0]][3] += 1
    if arguments.verbose: print("")
    HCOMMON.snapshoot(start_t, "dup", arguments.verbose)
# =============================================================================
# sort for outgoing edges  ----------------------------------------------------
    start_t = HCOMMON.snaptime()

    start_points.sort(key=lambda x: x[3], reverse=True)

    HCOMMON.snapshoot(start_t, "sort", arguments.verbose)
# =============================================================================
# write to json file ----------------------------------------------------------
    filename = arguments.file
    filename = "startpoints/" + filename.split("/",1)[-1] # change path
    # substitute "instance" with "sky-#edges"
    filename = filename.split(".",1)[0] + ".sky-" + str(len(start_points)) + ".json"
    data = {
            "type": "Startpoints",
            'instance_name' : instance,
            "points": []
        }
    for s in start_points:
        data['points'].append({'x': s[0], 'y': s[1]})

    if arguments.verbose: print("Duplicates %d%%" % (100 - int((len(start_points)/len(s_edges))*100)))

    if arguments.plot:
        for p in instance_points:
            plt.plot(p[0],p[1],"b.")
        for i,p in enumerate(start_points):
            plt.plot(p[0],p[1],"rP")
            if (i+1) >= arguments.plot: break
        plt.show()

    with open(filename, 'w') as json_file:
                json.dump(data, json_file)
