import matplotlib
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import json
import bisect
import scipy
import argparse
import sys
import time
import math
import numpy as np

sys.path.append('./bin')
import HJSON
import HCOMMON

def insort(ml, e):
    if len(ml) == 0:
        #print("insert " + str(e[0]))
        return [e]
    if len(ml) == 1:
        if ml[0][0] < e[0]:
            ml.append(e)
            #print("append " + str(e[0]))
        #else:
            #print("drop " + str(e[0]))
        return ml
    if len(ml) > 1:
        mid = math.floor(len(ml)/2)
        if e[0] <= ml[mid][0]:
            #print(str(e[0]) + " < " + str(ml[mid][0]))
            out = insort(ml[:mid], e) + ml[mid:]
        else:
            #print(str(e[0]) + " > " + str(ml[mid][0]))
            out = ml[:mid] + insort(ml[mid:], e)
        return out

if __name__ == "__main__":
    matplotlib.use('TkAgg')
# =============================================================================
# setup -----------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Bens Algorithm for SoCG')
    parser.add_argument('file')
    parser.add_argument('-s', type=int, nargs='?', default=100, dest='sky',
                        help='Only the sky is the limit.')
    parser.add_argument('-v', action='store_true', dest='verbose',
                        help='Print debug messages, if you must')
    parser.add_argument('-p', type=int, nargs='?', default=0, dest='plot',
                        help='Plot, if you must')
    arguments = parser.parse_args()

    instance_points,instance = HJSON.readTestInstance(arguments.file)
# =============================================================================
# triangulation of instance points  -------------------------------------------
    start_t = HCOMMON.snaptime()
    t_tri = Delaunay(instance_points)
    HCOMMON.snapshoot(start_t, "delaunay", arguments.verbose)
    start_t = HCOMMON.snaptime()

    t_midpoints = []
    t_midpoints =[[0,0,0]]
    for i,sim in enumerate(t_tri.simplices):
        if arguments.verbose: print("\r%.2f%%" % ((i/len(t_tri.simplices))*100), end="")
        e = [0,0,0]
        for i in range(len(sim)): # get midpoint for every simplex
            e[1] += instance_points[sim[i]][0]
            e[2] += instance_points[sim[i]][1]
        e = [0, int(e[1] / (i+1)), int(e[2] / (i+1))]
        """ #distance
        for i in range(len(sim)): # insertion by longest distance
            dist = np.linalg.norm(np.array(instance_points[sim[i]]) - np.array((e[1], e[2])))
            e[0] = max(e[0], dist)
        """ #area of triangle: 0,5 * ||AB^AC||
        e[0] = 0.5 * np.linalg.norm(np.cross(np.array(instance_points[sim[1]])-np.array(instance_points[sim[0]]),
                                             np.array(instance_points[sim[2]])-np.array(instance_points[sim[0]])))
        #"""
        #t_midpoints.append(e)
        t_midpoints = insort(t_midpoints, e)
    if arguments.verbose: print("\r", end="")
    t_midpoints.pop(0)
    t_midpoints.reverse()
    #t_midpoints.sort(key=lambda x:x[0], reverse=True)
    HCOMMON.snapshoot(start_t, "midpoints red", arguments.verbose)
# =============================================================================
# write to json file ----------------------------------------------------------
    filename = arguments.file
    filename = "startpoints/" + filename.split("/",1)[-1] # change path
    # substitute "instance" with "sky-#edges"
    filename = filename.split(".",1)[0] + ".sky-" + str(len(t_midpoints)) + ".json"
    data = {
            "type": "Startpoints",
            'instance_name' : instance,
            "points": []
        }
    for s in t_midpoints:
        data['points'].append({'x': s[0], 'y': s[1]})

    #if arguments.verbose: print("Duplicates %d%%" % (100 - int((len(start_points)/len(s_edges))*100)))

    if arguments.plot:
        #fi, ax = plt.subplots()
        for p in instance_points:
            plt.plot(p[0],p[1],"b.")
        for i,p in enumerate(t_midpoints):
            plt.plot(p[1],p[2],"rP")
            #ax.add_artist(plt.Circle((p[1],p[2]), p[0],fill=False, color='r'))
            if (i+1) >= arguments.plot: break
        plt.show()

    with open(filename, 'w') as json_file:
        json.dump(data, json_file)
