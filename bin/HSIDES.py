from numpy import arccos, array, dot, pi, cross
from numpy.linalg import det, norm
from HDCEL import *
from itertools import product

def distance(v1, v2):
    return math.sqrt( (v2.x() - v1.x())**2 + ( v2.y() - v1.y())**2 )

def line_point_distance(l1, l2, p):
    l1l2 = [l2.x()-l1.x(), l2.y()-l1.y()]
    u = (p.x()-l1.x()) * (l2.x()-l1.x()) + (p.y()-l1.y()) * (l2.y()-l1.y())
    u = u / ( abs( math.sqrt( l1l2[0]**2 + l1l2[1]**2 ) )**2 )
    u = min(1, max(0, u))
    closest_point = Vertex( \
        explicit_x = l1.x() + u * l1l2[0],\
        explicit_y = l1.y() + u * l1l2[1] \
    )
    dist = distance(p, closest_point)
    return dist, closest_point, u

def hull_point_distance(hull, p):
    min_d = float('inf')
    for i in range(len(hull.convex_hull)):
        d, q, u = line_point_distance(hull.ch(i), hull.ch(i+1), p)
        if min_d>d:
            min_d = d
    assert(min_d<float('inf'))
    return min_d

def closest_point_hull(hull, p):
    min_d = float('inf')
    min_i = 0
    min_q = None
    for i in range(len(hull.convex_hull)):
        d, q, u = line_point_distance(hull.ch(i), hull.ch(i+1), p)
        if min_d>d or (min_d==d and u<1): # Prioritize the edge with its origin at q (u<1)
            min_d, min_i, min_q = d, i, q
    assert(min_q is not None and min_d<float('inf'))
    return min_d, min_i, min_q

def closest_point_hull2hull(static, fluid):
    min_d = float('inf')
    min_i = 0
    min_oi = 0
    min_q = None
    for i in range(len(static.convex_hull)):
        d, oi, q = closest_point_hull(fluid, static.ch(i))
        if d<min_d:
            min_d, min_i, min_oi, min_q = d, i, oi, q
    assert(min_q is not None and min_d<float('inf'))
    return min_d, min_i, min_oi, min_q

def isLeftOf(a, b, v, strict=False):
    """ (Orient.test) Returns true if v is to the left of a line from a to b. Otherwise false. """
    if strict: return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) > 0
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) >= 0

def get_intermediate_with_normal(static, fluid, static_i, fluid_i, fluid_q):
    inter = Vertex(\
        explicit_x = (static.ch(static_i).x() + fluid_q.x()) * 0.5,\
        explicit_y = (static.ch(static_i).y() + fluid_q.y()) * 0.5 \
    )

    points_to_test = [(static_i-1, static, fluid),(static_i+1, static, fluid)]
    if fluid_q.x()==fluid.ch(fluid_i).x() and fluid_q.y()==fluid.ch(fluid_i).y():
        points_to_test.append((fluid_i-1, fluid, static))
        points_to_test.append((fluid_i+1, fluid, static))
    else:
        points_to_test.append((fluid_i-1, fluid, static))
        points_to_test.append((fluid_i, fluid, static))

    for (i, hull, other) in points_to_test:
        if isLeftOf(hull.ch(i), hull.ch(i+1), inter):
            points_to_test.remove((i, hull, other))

    min_d = float('inf')
    min_q = None
    min_p = None
    for (i, hull, other) in points_to_test:
        d, _, q = closest_point_hull(other, hull.ch(i))
        if d<min_d:
            min_d, min_q, min_p = d, q, hull.ch(i)
    normal = Vertex(\
        explicit_x = (min_p.x() + min_q.x()) * 0.5,\
        explicit_y = (min_p.y() + min_q.y()) * 0.5 \
    )
    if fluid.intersects(inter, normal, isSegment=False): # Exceptions may trigger this. Sets partition line parellel to fluid_i
        #print("WARN: Unfair partition during merge.")
        normal = Vertex(\
            explicit_x = inter.x() + fluid.ch(fluid_i+1).x() - fluid.ch(fluid_i).x(),\
            explicit_y = inter.y() + fluid.ch(fluid_i+1).y() - fluid.ch(fluid_i).y(), \
        )
        if fluid.intersects(inter, normal, isSegment=False):
            pass
            #print("ERR: Invalid partition.")
    return inter, normal

def intermediate_point(this, other):
    md1, mi1, moi1, mq1 = closest_point_hull2hull(this, other)
    md2, mi2, moi2, mq2 = closest_point_hull2hull(other, this)
    if md1<md2:
        return get_intermediate_with_normal(this, other, mi1, moi1, mq1)
    else:
        return get_intermediate_with_normal(other, this, mi2, moi2, mq2)
