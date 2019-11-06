"""@package docstring
Software project for the Computational Geometry Week 2020 competition
"""

import matplotlib.pyplot as plt
import json
import math
import sys
import DCEL
from DCEL import Vertex

convex_hull = []
def ch(i):
    return convex_hull[i % len(convex_hull)]

def ch_i(i):
    return i % len(convex_hull)

### Helper Functions

def readTestInstance(filename):
    """ reads a test instance file by name
    input:      filename as string
    returns:    points as dictionary of lists 'x' and 'y'
                instance name as string
    """
    points = {'x': [], 'y': []}
    with open(filename) as json_file:
        data = json.load(json_file)
        for p in data['points']:
            points['x'].append(int(p['x']))
            points['y'].append(int(p['y']))
            # print('%i: (%.1f | %.1f)' % (int(p['i']), float(p['x']), float(p['y'])))
        instance = data['name']
        return points, instance

def writeTestSolution(filename, instance, edges=[]):
    """ writes edges to a solution file
    input:      filename as string
                instance name as string
                list of edges by indices of points
    """
    filename = filename.split(".",1)[0] + ".solution.json"

    data = {
        'type':'Solution',
        'instance_name' : instance,
        'meta' : {'comment':''},
        'edges' : []
    }
    for index,val in enumerate(edges['in']):
        data['edges'].append({
            'i': str(edges['in'][index]),
            'j': str(edges['out'][index]),
        })

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

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
    degree = None
    if edges != None:
        degree = [0]*len(points['x'])
        for ein in edges['in']:
            degree[ein] += 1
        for eout in edges['out']:
            degree[eout] += 1
        for index,val in enumerate(degree): #TODO leftover
            degree[index] >>= 1

    for i,val in enumerate(points['x']):
        plt.plot(points['x'][i], points['y'][i], col(color,degree,i)+'o')

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
            [points['x'][i], points['x'][j]],
            [points['y'][i], points['y'][j]],
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

def test_block(e=None, p=None):
    edges = DCEL.get_edge_dict()
    plt.cla()
    drawEdges(edges,points)
    drawPoints(points)
    drawHull()
    if e != None:
        drawSingleEdge(e)
    if p != None:
        drawSinglePoint(p)
    plt.draw()
    plt.pause(0.001)
    input("")

def usage():
    print("This program calculates solutions for SoCG contest")
    print("usage:\npython3 presentation.py <instance> [showcase] [<x-coordinates> <y-coordinates>]")
    print("\t<instance>\tis the filename of the instance file")
    print("\t[showcase]\tuse this argument to start visualization mode")
    print("\t[x-coordinates]\tof the starting point")
    print("\t[y-coordinates]\tof the starting point")
    sys.exit(1)

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
        print("ERROR: NON-VISIBLE-EDGE! Falling back to iterative result.")
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
    return math.sqrt( math.pow( v2.x() - v1.x(), 2) + math.pow( v2.y() - v1.y(), 2))

# Overwritten
def sortByDistance(vlist, p):
    """ Sorts a list of vertices by euclidean distance towards a reference vertex p """
    vlist.sort(key=lambda x: get_distance(x, p))

def getEdge(a, b):
    """ Note: will loop endlessly if a and b are not actually connected. """
    e = a.incidentEdge
    i = 0 # guard to prevent endless loop, i is at most |V| with V = E
    while e.nxt.origin != b and i <= len(points['x']):
        i += 1
        e = e.twin.nxt
    if i > len(points['x']):
        print("ERROR: Points (%i,%i) not connected" % (a.i, b.i))
    return e # edge e between vertices a and b

def update_convex_hull(i, j ,v):
    i = ch_i(i)
    j = ch_i(j)
    if j < i:
        convex_hull[i+1:len(convex_hull)] = [v]
        convex_hull[0:j] = []
    else:
        convex_hull[i+1:j] = [v]

def iterate(v, debug):
    i = getLeftMostVisibleIndex(v)
    j = i
    e = getEdge(ch(i), ch(i+1))

    while isVisibleEdge(e, v):
        n = e.nxt

        if debug == 1:
            test_block(e, v)

        top_is_convex = not isLeftOfEdge(e.twin.prev, v)
        bot_is_convex = not isLeftOfEdge(e.twin.nxt, v)

        e.origin.connect_to(v)
        if not isVisibleEdge(n, v):
            n.origin.connect_to(v) #This seems inefficient

        if top_is_convex and bot_is_convex:
            e.remove()

        e = n
        j += 1

    if debug == 1:
            test_block(e, v)
    update_convex_hull(i, j, v)
    if debug == 1:
            test_block(e, v)

### Main

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("ERROR: Not enough arguments")
        usage()
    if sys.argv[1] == "help" or sys.argv[1] == "/?" or sys.argv[1] == "?" or \
       sys.argv[1] == "--help" or sys.argv[1] == "-h":
        usage()
    try:
        f = open(sys.argv[1])
        f.close()
    except:
        print("ERROR: File %s does not exist" % (sys.argv[1]))
        usage()
    debug = 0
    if len(sys.argv) > 2 and sys.argv[2] == "showcase":
        debug = 1

    plt.rcParams["figure.figsize"] = (16,9)
    points,instance = readTestInstance(sys.argv[1])
    DCEL.points = points

    origin = Vertex(explicit_x=6500, explicit_y=4000)
    if len(sys.argv) > 4:
        origin = Vertex(explicit_x=int(sys.argv[3]), explicit_y=int(sys.argv[4]))
    vertices = [Vertex(index=i) for i in range(len(points['x']))]
    sortByDistance(vertices, origin)

    # Create the first triangle
    if isLeftOf(vertices[0], vertices[1], vertices[2]):
        convex_hull = [vertices[0], vertices[1], vertices[2]]
        DCEL.make_triangle(vertices[0], vertices[1], vertices[2])
    else:
        convex_hull = [vertices[0], vertices[2], vertices[1]]
        DCEL.make_triangle(vertices[0], vertices[2], vertices[1])

    for i in range(3, len(vertices)):
        iterate(vertices[i], debug)
        sys.stdout.flush()

    edges = DCEL.get_edge_dict()

    drawEdges(edges,points)
    drawPoints(points,edges)
    writeTestSolution(sys.argv[1],instance,edges)
    plt.show()
