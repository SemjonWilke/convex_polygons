"""@package docstring
Software project for the Computational Geometry Week 2020 competition
"""

import matplotlib.pyplot as plt
import json

### Helper Functions

def readtestinstance(filename):
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

def writetestsolution(filename, instance, edges=[]):
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

def drawpoints(points, color='r.'):
    """ draws points to plt
    input:      points as dictionary of lists 'x' and 'y'
                color of points (matplotlib style)
    """
    for i,val in enumerate(points['x']):
        plt.plot(points['x'][i], points['y'][i], color)

def drawedges(edges, points, color='b-'):
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

""" maybe dont implement dcel but use https://github.com/anglyan/dcel """

def connect_to(v, x):
    """ forms a DCEL connection from v to x"""
    return # void
    
def remove(edge):
    """    if(origin.IncidentEdge==this) //TODO: set origin.IncidentEdge to an arbitrary Edge incident from origin
        if(twin.origin.IncidentEdge==this) //TODO: twin.origin.IncidentEdge to an arbitrary Edge incident from twin.origin
       
        next.prev = twin.prev;
        prev.next = twin.next;
        twin.remove();
    """
    return #void

def  center(Vertex a, Vertex b, Vertex c):
    """ Returns centroid (geometric center) of a triangle △abc """
    """float avg_x=(a.x+b.x+c.x)/3;
    float avg_y=(a.y+b.y+c.y)/3;
    return new Vertex(avg_x,avg_y);"""
    return # Vertex
    
def getSomeVisibleSegment(Vertex p):
    """ Returns index of some segment on the convex hull visible from p """
    """Vertex c = center(convex_hull[0], convex_hull[1], convex_hull[2]);
    int min = 0;
    int max = convex_hull.length - 1;
    int i = Math.ceil((max-min)/2);

    while(max>min) {
    i = min + Math.ceil((max-min)/2);
    if(isVisible(i, p)) {
        return i;
    }
    if(isLeftOf(c, convex_hull[i], p)) {
        min = i+1;
    }
    else {
        max = i-1;
    }
    }
    if(isVisible(max+1, p)) return max+1;
    if(isVisible(max-1, p)) return max-1;
    return max;"""
    return # int max
    
def sortByDistance(input, origin):
    """ Returns a list of vertices sorted by euclidean distance to origin. """
    return #vertex list

def isLeftOf(l1, l2, x):
    """ (Orientierungstest) Returns true if x is to the left of a line from l1 to l2. Otherwise false. """
    """return ((l2.x - l1.x)*(x.y - l1.y) - (l2.y - l1.y)*(x.x - l1.x)) <= 0;"""
    return #bool

def isLeftOfedge(e, x):
    """ Same as above but takes an Edge as parameter instead of two points """
    """return isLeftOf(e.origin, e.next.origin, x);"""
    return #bool

def isVisible(index, vertex):
    """ Returns true if the i'th segment of the convex_hull is visible from x """
    """return !isLeftOf(convex_hull[index], convex_hull[index+1], vertex); # decide if convex_hull should be global"""
    return #bool

def getLeftMostVisibleIndex(vertex):
    """ Returns the index of vertex on the convex hull furthest 'to the left' visible from x """
    """int some = getSomeVisibleSegment(x);
    while(isVisible(some-1, x)) some--;
    return some;"""
    return #index of vertex

def get_edge(a, b):
    """ Note: will loop endlessly if a and b are not actually connected. """
    """
    Edge e = v1.IncidentEdge;
    while(e.next.origin != v2) {
        e = e.twin.next;
    }
    """
    return # edge e between vertices a and b

def iterate(p):
    """int i = getLeftMostVisibleIndex();
    int j = i;
 
    Vertex v1 = convex_hull[i];
    Vertex v2 = convex_hull[i+1];
 
    Edge e = get_edge(v1, v2);
 
    while(isVisible(e)) {
        Edge n = e.next;
 
        bool top_is_convex = !isLeftOf(e.twin.prev, p)
        bool bottom_is_convex = !isLeftOf(e.twin.next, p)
 
        e.origin.connect_to(p);
        n.origin.connect_to(p);
 
        if(top_is_convex && bottom_is_convex) e.remove();
 
        e = n;
        j++;
    }
    //TODO: replace indeces i to j in convex_hull with just p.
    """
    return # void
    
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
    TODO: translate to python
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
