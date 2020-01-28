import sys
import math

import HDCEL
import HCLEAN
from HDCEL import isLeftOf, isRightOf, isLeftOfEdge, isRightOfEdge, are_colinear

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

    v1, v2, v3 = vertices[0], vertices[1], vertices[2]

    # Create the first triangle
    it = 3
    skipped = []
    if are_colinear(v1, v2, v3): #Weirdo case: If three closest verts are colinear -> cant make triangle
        if get_distance(v1, v2) < get_distance(v1, v3):
            while are_colinear(v1, v2, v3):
                skipped.append(v3)
                v3 = vertices[it]
                it += 1
        else:
            while are_colinear(v1, v2, v3):
                skipped.append(v2)
                v2 = vertices[it]
                it += 1
        # Found a non-colinear triple!
        convex_hull = [v1, v2, v3]
        HDCEL.make_triangle(v1, v2, v3)
        for p in skipped:
            iterate(p) # Catch up with the points we skipped
    # Regular cases:
    elif isLeftOf(v1, v2, v3):
        convex_hull = [v1, v2, v3]
        HDCEL.make_triangle(v1, v2, v3)
    else:
        convex_hull = [v1, v3, v2]
        HDCEL.make_triangle(v1, v3, v2)

    # Run iterations
    for i in range(it, len(vertices)):
        iterate(vertices[i])
        sys.stdout.flush()
    HCLEAN.clean_edges()

def ch(i):
    return convex_hull[i % len(convex_hull)]

def ch_i(i):
    return i % len(convex_hull)

def  center(a, b, c):
    """ Returns centroid (geometric center) of a triangle  abc """
    avg_x = (a.x()+b.x()+c.x()) / 3
    avg_y = (a.y()+b.y()+c.y()) / 3
    return HDCEL.Vertex(explicit_x=avg_x, explicit_y=avg_y)

def isVisible(i, v):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return isRightOf(ch(i), ch(i+1), v, strict=True)

def isVisibleEdge(e, v):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return isRightOf(e.origin, e.nxt.origin, v, strict=True)

def getSomeVisibleSegment(v):
    """ Returns index of some segment on the convex hull visible from v """
    for i in range(len(convex_hull)):
        if isVisible(i, v):
            return i

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
    for e in a.get_connected_edges():
        if e.nxt.origin == b:
            return e
    if verbose: print("INFO: Points (%i,%i) not connected" % (a.i, b.i))
    return None

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
