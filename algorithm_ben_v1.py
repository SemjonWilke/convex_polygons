import sys
import math

import HDCEL

convex_hull = []
vertices = []
verbose = False

def run(_vertices, _origin, _verbose):
    global vertices, verbose, convex_hull
    vertices = _vertices
    verbose = _verbose

    if verbose: print("Bens Algorithm")
    if verbose: print("Start points are (%i|%i)" % (_origin.explicit_x, _origin.explicit_y))
    sortByDistance(vertices, _origin)

    # Create the first triangle
    if isLeftOf(vertices[0], vertices[1], vertices[2]):
        convex_hull = [vertices[0], vertices[1], vertices[2]]
        HDCEL.make_triangle(vertices[0], vertices[1], vertices[2])
    else:
        convex_hull = [vertices[0], vertices[2], vertices[1]]
        HDCEL.make_triangle(vertices[0], vertices[2], vertices[1])

    # Run iterations
    for i in range(3, len(vertices)):
        iterate(vertices[i])
        sys.stdout.flush()


def ch(i):
    return convex_hull[i % len(convex_hull)]

def ch_i(i):
    return i % len(convex_hull)

def  center(a, b, c):
    """ Returns centroid (geometric center) of a triangle  abc """
    avg_x = (a.x()+b.x()+c.x()) / 3
    avg_y = (a.y()+b.y()+c.y()) / 3
    return HDCEL.Vertex(explicit_x=avg_x, explicit_y=avg_y)

def isLeftOf(a, b, v, strict=False):
    if strict: return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) > 0
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) >= 0

def isRightOf(a, b, v, strict=False):
    return not isLeftOf(a, b, v, strict=not strict)

def isLeftOfEdge(e, v, strict=False):
    return isLeftOf(e.origin, e.nxt.origin, v, strict)

def isRightOfEdge(e, v, strict=False):
    return isLeftOf(e.origin, e.nxt.origin, v, strict)

def isVisible(i, v):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return isRightOf(ch(i), ch(i+1), v, strict=True)

def isVisibleEdge(e, v):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return isRightOf(e.origin, e.nxt.origin, v, strict=True)

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
    while e.nxt.origin != b and i <= len(vertices):
        i += 1
        e = e.twin.nxt
    if i > len(vertices):
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

        top_is_convex = isRightOfEdge(e.twin.prev, v, strict=False)
        bot_is_convex = isRightOfEdge(e.twin.nxt, v, strict=False)

        e.origin.connect_to(v)
        if not isVisibleEdge(n, v):
            n.origin.connect_to(v) #This seems inefficient

        if top_is_convex and bot_is_convex:
            e.remove()

        e = n
        j += 1

    update_convex_hull(i, j, v)
