"""@package docstring
Software project for the Computational Geometry Week 2020 competition
"""

import matplotlib.pyplot as plt
import json
import math

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

### Algorithm functions

def  center(a, b, c): #untested
    """ Returns centroid (geometric center) of a triangle △abc """
    avg_x = (points[x][a.index]+points[x][b.index]+points[x][c.index]) / 3
    avg_y = (points[y][a.index]+points[y][b.index]+points[y][c.index]) / 3
    return Vertex(avg_x, avg_y)

def isLeftOf(a, b, v): #untested
    """ (Orientierungstest) Returns true if v is to the left of a line from a to b. Otherwise false. """
    if( (points[x][b.index] - points[x][a.index])*(points[y][v.index] - points[y][a.index]) - \
        (points[y][b.index] - points[y][a.index])*(points[x][v.index] - points[x][a.index]) <= 0):
        return True
    return False

def isLeftOfEdge(e, v): #untested
    """ Same as above but takes an Edge as parameter instead of two points """
    return isLeftOf(e.origin, e.next.origin, v)

def isVisible(i, v): #untested
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    if isleftof(convex_hull[i], convex_hull[i+1],v):
        return False
    return True

def getSomeVisibleSegment(v): #untested
    """ Returns index of some segment on the convex hull visible from v """
    min = 0
    max = len(convex_hull) - 1
    i = math.ceil((max-min)/2)

    while max > min:
        i = min + math.ceil((max-min)/2)
        if isVisible(i, v):
            return i

        if isLeftOf(center(convex_hull[0], convex_hull[1], convex_hull[2]), \
                    convex_hull[i], v):
            min = i + 1
        else:
            max = i - 1

    if isVisible(max + 1, v)
        return max + 1
    if isVisible(max - 1, v)
        return max - 1
    return max

def getLeftMostVisibleIndex(v): #untested
    """ Returns the index of vertex v on the convex hull furthest 'to the left' visible from v """
    some = getSomeVisibleSegment(v)
    while isVisible(some-1, v):
        some -= 1
    return some

def sortByDistance(input, origin): #TODO
    """ Returns a list of vertices sorted by euclidean distance to origin. """
    return #vertex list

def getEdge(a, b): #untested
    """ Note: will loop endlessly if a and b are not actually connected. """
    e = a.IncidentEdge
    i = 0 # guard to prevent endless loop, i is at most |V| with V = E
    while e.next.origin != b || i <= max(points[x]):
        i += 1
        e = e.twin.next
    return e # edge e between vertices a and b

def iterate(v): #untested
    i = getLeftMostVisibleIndex(v)
    e = getEdge(convex_hull[i], convex_hull[i+1])

    while isVisible(e, v):
        n = e.next

        top_is_convex = !isLeftOf(e.twin.prev, v)
        bot_is_convex = !isLeftOf(e.twin.next, v)

        e.origin.connectTo(v) # TODO function call an DCEL anpassen
        n.origin.connectTo(v) # TODO function call

        if top_is_convex && bot_is_convex:
            e.remove() # TODO function call

        e = n # TODO unsicher ob das klappt (ist ja kein pointer in python)

### Main

if __name__ == '__main__':
    points,instance = readtestinstance('euro-night-0000100.instance.json')
    drawpoints(points)
    #''' delete # to switch comments and have an example
    edges = {'in' : [], 'out' : []}
    '''
    edges = {'in' : [1,3,5,7,9], 'out' : [0,2,4,6,8]} # example
    #'''

    """
    Q = sortByDistance(input, origin);

    first_triangle = [];
    if(isLeftOf(Q[0], Q[1], Q[2])) {
        convex_hull = [Q[0], Q[1], Q[2]];
        Q[0].connect_to(Q[1]);
        Q[1].connect_to(Q[2]);
        Q[2].connect_to(Q[0]);
    }
    else {
        convex_hull = [Q[0], Q[2], Q[1]];
        Q[0].connect_to(Q[2]);
        Q[2].connect_to(Q[1]);
        Q[1].connect_to(Q[0]);
    }

    for(int i=3; i<Q.length; i++) iterate(Q[i]);
    """

    drawedges(edges,points)
    writetestsolution('euro-night-0000100.solution.json',instance)
    plt.show()
