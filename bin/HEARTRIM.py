from HDCEL import *

def isLeftOfEdge(e, v):
    """ Same as above but takes an Edge as parameter instead of two points """
    return isLeftOf(e.origin, e.nxt.origin, v)

def isLeftOf(a, b, v, strict=False):
    """ (Orient.test) Returns true if v is to the left of a line from a to b. Otherwise false. """
    if strict: return ((b.x - a.x)*(v.y - a.y) - (b.y - a.y)*(v.x - a.x)) > 0
    return ((b.x - a.x)*(v.y - a.y) - (b.y - a.y)*(v.x - a.x)) >= 0

def m_sign (p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

def PointInTriangle (pt, v1, v2, v3):
    d1 = m_sign(pt, v1, v2);
    d2 = m_sign(pt, v2, v3);
    d3 = m_sign(pt, v3, v1);

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0);
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0);

    return not (has_neg and has_pos);

def isEar(e): # with respect to e.origin
    if isLeftOfEdge(e.prev, e.nxt.origin): return False # Non-convex connextion
    for v in area(e):
        if v!=e.prev.origin and v!=e.origin and v!=e.nxt.origin and PointInTriangle(v, e.prev.origin, e.origin, e.nxt.origin):
            return False
    return True

def earTrimArea(e):
    while e.prev != e.nxt.nxt:
        e = earTrim(e)

def earTrim(e):
    while not isEar(e):
        e=e.nxt
    return e.prev.origin.connect_to(e.nxt.origin)
