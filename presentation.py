"""@package docstring
Software project for the Computational Geometry Week 2020 competition
"""

import matplotlib.pyplot as plt
import random
import json
import math
import sys
import DCEL
from DCEL import Vertex
import time
import argparse

convex_hull = []
def ch(i):
    return convex_hull[i % len(convex_hull)]

def ch_i(i):
    return i % len(convex_hull)

### Helper Functions

def readTestInstance(filename):
    """ reads a test instance file by name
    input:      filename as string
    returns:    points as array of coordinates
                instance name as string
    """
    points = []
    with open(filename) as json_file:
        data = json.load(json_file)
        for p in data['points']:
            points.append([int(p['x']), int(p['y'])])
        instance = data['name']
        json_file.close()
        return points, instance

def pointdegree(edges):
    degree = None
    if edges != None:
        degree = [0]*len(points)
        for ein in edges['in']:
            degree[ein] += 1
        for eout in edges['out']:
            degree[eout] += 1
    return degree

def getmeta(filename, edges, coord):

    degrees = pointdegree(edges)

    noclose = True
    iteration = 0
    edgenum = len(edges['in'])
    degavg = sum(degrees)/len(degrees)
    degmax = max(degrees)
    edgenumbetter = 0
    degavgov = degavg
    degmaxov = degmax
    try:
        solutionfp = open(filename, 'r')
    except:
        if verbose: print("No previous solution existing in %s" % filename)
        noclose = False

    if noclose:
        data = json.load(solutionfp)
        try: iteration = int(data['meta']['iteration']) + 1
        except: pass
        try: edgenumbetter = int(data['meta']['edges']) - edgenum
        except: pass
        try: degavgov = float(data['meta']['degree_avg_overall']) + degavg
        except: pass
        try: degmaxov = max(int(data['meta']['degree_max_overall']), degmaxov)
        except: pass
        solutionfp.close()
    return { 'comment' : '', 'iteration' : str(iteration), 'coordinates' : str(coord), 'edges' : str(edgenum), \
            'degree_avg' : str(degavg), 'deg_max' : str(degmax), 'edges_better' : str(edgenumbetter), \
            'degree_avg_overall' : str(degavgov), 'degree_max_overall' : str(degmaxov) }

def writeTestSolution(filename, instance, coord, edges=[], overwrite=False):
    """ writes edges to a solution file
    input:      filename as string
                instance name as string
                list of edges by indices of points
    """


    filename = "solutions/" + filename.split("/",1)[-1] # fix path
    filename = filename.split(".",1)[0] + ".solution.json" # substitute "instance" with "solution"
    meta = getmeta(filename, edges, coord)
    better = int(meta['edges_better'])

    fexist = True
    try:
        fp = open(filename, 'r')
        fp.close()
    except:
        fexist = False

    if better > 0: # overwrite if its better else discard
        if verbose: print("Found a stronger solution by %s edges" % better)

    data = {
        'type':'Solution',
        'instance_name' : instance,
        'meta' : meta,
        'edges' : []
    }

    for index,val in enumerate(edges['in']):
        data['edges'].append({
            'i': str(edges['in'][index]),
            'j': str(edges['out'][index]),}
        )

    if not fexist or (fexist and better > 0 and overwrite):
        with open(filename, 'w') as json_file:
            json.dump(data, json_file)
        if verbose: print("Solution written to %s" % (filename))
    if fexist and better <= 0:
        if verbose: print("Solution was weaker by %s edges" % abs(better))

def col(color, degree, index):
    if degree == None:
        return color
    if degree[index] == 0 or degree[index] == 1:
        return 'w' #white
    if degree[index] == 2:
        return 'g' #green
    if degree[index] == 3:
        return 'y' #yellow
    if degree[index] >= 4:
    #    return 'c' #cyan
    #if degree[index] == 5:
    #    return 'm' #magenta
    #if degree[index] >= 6:
        return 'r' #red

def drawPoints(points, edges=None, color='r'):
    """ draws points to plt
    input:      points as dictionary of lists 'x' and 'y'
                color of points (matplotlib style)
    """
    degree = pointdegree(edges)
    for i,val in enumerate(points):
        plt.plot(val[0], val[1], col(color,degree,i)+'o')

def drawEdges(edges, points, color='b-'):
    """ draws edges to plt
    input:      list of edges indexing points
                points as dictionary of lists 'x' and 'y'
                color of edges (matplotlib style)
    """
    for index,val in enumerate(edges['in']):
        i = edges['in'][index]
        j = edges['out'][index]
        plt.plot(
            [points[i][0], points[j][0]],
            [points[i][1], points[j][1]],
            color
        )

def drawHull():
    for i in range(len(convex_hull)):
        plt.plot([ch(i).x(), ch(i+1).x()], [ch(i).y(), ch(i+1).y()], 'r-')

def drawSingleEdge(e):
    plt.plot([e.origin.x(), e.nxt.origin.x()], [e.origin.y(), e.nxt.origin.y()], 'g-')
    plt.plot(e.origin.x(), e.origin.y(), 'bo')
    plt.plot(e.nxt.origin.x(), e.nxt.origin.y(), 'yo')

def drawSinglePoint(v):
    plt.plot(v.x(), v.y(), 'ks')

def randomstart(seed=None):
    random.seed(seed, 2)
    if seed != None:
        if verbose: print("Fixed seed is: %s" % str(seed))
    xmin,ymin = min([p[0] for p in points]),min([p[1] for p in points])
    xmax,ymax = max([p[0] for p in points]),max([p[1] for p in points])
    return (random.randint(ymin, ymax), random.randint(xmin, xmax))

def snapshoot(start_t, msg):
    elp_t = time.process_time() - start_t
    if verbose: print("%s time: %02.0f:%02.0f:%2.2f h" % (msg, elp_t/3600, elp_t/60, elp_t))

### Algorithm functions

def  center(a, b, c):
    """ Returns centroid (geometric center) of a triangle abc """
    avg_x = (a.x()+b.x()+c.x()) / 3
    avg_y = (a.y()+b.y()+c.y()) / 3
    return Vertex(explicit_x=avg_x, explicit_y=avg_y)

def isLeftOf(a, b, v):
    """ (Orient.test) Returns true if v is to the left of a line from a to b. Otherwise false. """
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) >= 0

def isLeftOfEdge(e, v):
    """ Same as above but takes an Edge as parameter instead of two points """
    return isLeftOf(e.origin, e.nxt.origin, v)

def isVisible(i, v):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return not isLeftOf(ch(i), ch(i+1), v)

def isVisibleEdge(e, v):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return not isLeftOf(e.origin, e.nxt.origin, v)

def getSomeVisibleSegment(v):
    """ Returns index of some segment on the convex hull visible from v """
    min = 0
    max = len(convex_hull) - 1
    i = math.ceil((max - min) / 2)

    while max > min:
        i = min + math.ceil((max - min) / 2)
        if isVisible(i, v):
            return i

        if isLeftOf(center(ch(0), ch(1), ch(2)), ch(i), v):
            min = i + 1
        else:
            max = i - 1

    if isVisible(max + 1, v):
        return max + 1
    if isVisible(max - 1, v):
        return max - 1
    if not isVisible(max, v):
        if verbose: print("INFO: NON-VISIBLE-EDGE! Falling back to iterative result.")
        for i in range(len(convex_hull)):
            if isVisible(i, v):
                return i
    return max

def getLeftMostVisibleIndex(v):
    """ Returns the index of vertex v on the convex hull furthest 'to the left' visible from v """
    some = getSomeVisibleSegment(v)
    while isVisible(some - 1, v):
        some -= 1
    return some

# Inserted
def get_distance(v1, v2):
    return (v2.x() - v1.x())**2 + ( v2.y() - v1.y())**2

# Overwritten
def sortByDistance(vlist, p):
    """ Sorts a list of vertices by euclidean distance towards a reference vertex p """
    vlist.sort(key=lambda x: get_distance(x, p))

def getEdge(a, b):
    e = a.incidentEdge
    i = 0 # guard to prevent endless loop, i is at most |V| with V = E
    while e.nxt.origin != b and i <= len(points):
        i += 1
        e = e.twin.nxt
    if i > len(points):
        if verbose: print("INFO: Points (%i,%i) not connected" % (a.i, b.i))
    return e # edge e between vertices a and b

def update_convex_hull(i, j ,v):
    i = ch_i(i)
    j = ch_i(j)
    if j < i:
        convex_hull[i+1:len(convex_hull)] = [v]
        convex_hull[0:j] = []
    else:
        convex_hull[i+1:j] = [v]

def iterate(v):
    i = getLeftMostVisibleIndex(v)
    j = i
    e = getEdge(ch(i), ch(i+1))

    while isVisibleEdge(e, v):
        n = e.nxt

        top_is_convex = not isLeftOfEdge(e.twin.prev, v)
        bot_is_convex = not isLeftOfEdge(e.twin.nxt, v)

        e.origin.connect_to(v)
        if not isVisibleEdge(n, v):
            n.origin.connect_to(v) #This seems inefficient

        if top_is_convex and bot_is_convex:
            e.remove()

        e = n
        j += 1

    update_convex_hull(i, j, v)

### Main
def run(filename, c=(6000, 4500), overwrite=False, plot=False):
    global convex_hull
    global points

    if plot:
        plt.rcParams["figure.figsize"] = (16,9)

    start_t = time.process_time()
    DCEL.points = points

    origin = Vertex(explicit_x=c[0], explicit_y=c[1])
    if verbose: print("Start points are (%i|%i)" % (origin.explicit_x, origin.explicit_y))

    vertices = [Vertex(index=i) for i in range(len(points))]
    sortByDistance(vertices, origin)

    # Create the first triangle
    if isLeftOf(vertices[0], vertices[1], vertices[2]):
        convex_hull = [vertices[0], vertices[1], vertices[2]]
        DCEL.make_triangle(vertices[0], vertices[1], vertices[2])
    else:
        convex_hull = [vertices[0], vertices[2], vertices[1]]
        DCEL.make_triangle(vertices[0], vertices[2], vertices[1])

    for i in range(3, len(vertices)):
        iterate(vertices[i])
        sys.stdout.flush()

    edges = DCEL.get_edge_dict(verbose)

    snapshoot(start_t, "Computation")
    writeTestSolution(sys.argv[1],instance,c,edges,overwrite)

    if plot:
        start_t = time.process_time()
        drawEdges(edges,points)
        drawPoints(points,edges)
        snapshoot(start_t, "Plotting")
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bens Algorithm for SoCG')
    parser.add_argument('file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--coordinates', type=int, nargs=2, dest='coord', help='Coordinates of starting point')
    group.add_argument('-r', '--random', nargs='?', default=0, dest='rndm', help='Use random starting point with optional seed')
    parser.add_argument('-o', '--overwrite', action='store_true', dest='overwrite', help='Overwrite existing solution if better')
    parser.add_argument('-p', '--plot', action='store_true', dest='plot', help='Show plot')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Print human readable information')
    arguments = parser.parse_args()

    verbose = arguments.verbose
    points,instance = readTestInstance(arguments.file)
    if arguments.coord != None:
        run(arguments.file, arguments.coord, arguments.overwrite, arguments.plot)
    else:
        run(arguments.file, randomstart(arguments.rndm), arguments.overwrite, arguments.plot)
