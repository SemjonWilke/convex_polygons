"""@package docstring
Software project for the Computational Geometry Week 2020 competition
"""

import matplotlib.pyplot as plt
import json
import math
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
    data = {
        'type':'Solution',
        'instance_name' : instance,
        'meta' : {'comment':''},
        'edges' : []
    }
    for edge in edges:
        data['edges'].append({
            'i': str(edge['in']),
            'j': str(edge['out']),
        })

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def drawPoints(points, color='r.'):
    """ draws points to plt
    input:      points as dictionary of lists 'x' and 'y'
                color of points (matplotlib style)
    """
    for i,val in enumerate(points['x']):
        plt.plot(points['x'][i], points['y'][i], color)

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

### Algorithm functions

def  center(a, b, c): #untested
    """ Returns centroid (geometric center) of a triangle abc """
    avg_x = (a.x()+b.x()+c.x()) / 3
    avg_y = (a.y()+b.y()+c.y()) / 3
    return Vertex(explicit_x=avg_x, explicit_y=avg_y)

def isLeftOf(a, b, v): #untested
    """ (Orient.test) Returns true if v is to the left of a line from a to b. Otherwise false. """
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) > 0

def isLeftOfEdge(e, v): #untested
    """ Same as above but takes an Edge as parameter instead of two points """
    return isLeftOf(e.origin, e.nxt.origin, v)

def isVisible(i, v): #untested
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return not isLeftOf(ch(i), ch(i+1), v)

def isVisibleEdge(e, v): #untested
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return not isLeftOf(e.origin, e.nxt.origin, v)

def getSomeVisibleSegment(v): #untested
    """ Returns index of some segment on the convex hull visible from v """
    min = 0
    max = len(convex_hull) - 1
    i = math.ceil((max-min)/2)

    while max > min:
        i = min + math.ceil((max-min)/2)
        if isVisible(i, v):
            return i

        if isLeftOf(center(ch(0), ch(1), ch(2)), \
                    ch(i), v):
            min = i + 1
        else:
            max = i - 1

    if isVisible(max + 1, v):
        return max + 1
    if isVisible(max - 1, v):
        return max - 1
    if not isVisible(max, v):
        print("ERROR: NON-VISIBLE-EDGE! FALLING BACK TO ITERATIVE RESULT")
        for i in range(len(convex_hull)):
            if isVisible(i, v): return i
    return max

def getLeftMostVisibleIndex(v): #untested
    """ Returns the index of vertex v on the convex hull furthest 'to the left' visible from v """
    some = getSomeVisibleSegment(v)
    while isVisible(some-1, v):
        some -= 1
    return some

# Inserted
def get_distance(v1, v2):
    return math.sqrt( math.pow( v2.x() - v1.x(), 2) + math.pow( v2.y() - v1.y(), 2))

# Overwritten
def sortByDistance(vlist, p):
    """ Sorts a list of vertices by euclidean distance towards a reference vertex p """
    vlist.sort(key=lambda x: get_distance(x, p))

def getEdge(a, b): #untested
    """ Note: will loop endlessly if a and b are not actually connected. """
    e = a.incidentEdge
    i = 0 # guard to prevent endless loop, i is at most |V| with V = E
    while e.nxt.origin != b and i < len(points):
        i += 1
        e = e.twin.nxt
    if(i>=len(points) and e.nxt.origin != b): print("ERR: POINTS NOT CONNECTED")
    return e # edge e between vertices a and b

def update_convex_hull(i, j ,v):
    i = ch_i(i)
    j = ch_i(j)
    if(j<i):
        convex_hull[i+1:len(convex_hull)] = [v]
        convex_hull[0:j] = []
    else:
        convex_hull[i+1:j] = [v]

def iterate(v, b, vn): #untested
    #test_block()

    i = getLeftMostVisibleIndex(v)
    j = i
    e = getEdge(ch(i), ch(i+1))

    while isVisibleEdge(e, v):
        n = e.nxt

        #test_block(e)

        top_is_convex = not isLeftOfEdge(e.twin.prev, v)
        bot_is_convex = not isLeftOfEdge(e.twin.nxt, v)

        e.origin.connect_to(v)
        n.origin.connect_to(v)

        if top_is_convex and bot_is_convex:
            e.remove()

        e = n
        j+=1

    if(b): test_block(p=vn)
    update_convex_hull(i, j, v)
    #test_block()

### Main

def test_block(e=None, p=None):
    edges = DCEL.get_edge_dict()
    plt.cla()
    drawEdges(edges,points)
    drawHull()
    if(e!=None): drawSingleEdge(e)
    if(p!=None): drawSinglePoint(p)
    plt.draw()
    plt.pause(0.001)
    input("Press Enter to continue...")

if __name__ == '__main__':
    points,instance = readTestInstance('euro-night-0000100.instance.json')
    drawPoints(points)
    #''' delete # to switch comments and have an example
    edges = {'in' : [], 'out' : []}

    DCEL.points = points

    origin = Vertex(explicit_x=6500, explicit_y=4000)
    vertices = [Vertex(index=i) for i in range(len(points['x']))]
    sortByDistance(vertices, origin)
    #vertices = vertices[0:46]

    if(isLeftOf(vertices[0], vertices[1], vertices[2])):
        convex_hull = [vertices[0], vertices[1], vertices[2]]
        DCEL.make_triangle(vertices[0], vertices[1], vertices[2])
    else:
        convex_hull = [vertices[0], vertices[2], vertices[1]]
        DCEL.make_triangle(vertices[0], vertices[2], vertices[1])

    for i in range(3, len(vertices)-1): iterate(vertices[i], i>100, vertices[i+1])

    edges = DCEL.get_edge_dict()

    '''
    edges = {'in' : [1,3,5,7,9], 'out' : [0,2,4,6,8]} # example

    #'''

    drawEdges(edges,points)
    writeTestSolution('euro-night-0000100.solution.json',instance)
    plt.show()
