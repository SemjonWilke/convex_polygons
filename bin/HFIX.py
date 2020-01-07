import HDCEL
from HDCEL import Vertex
import HVIS
import HCLEAN


def getEdge(a, b):
    e = a.incidentEdge
    i = 0 # guard to prevent endless loop, i is at most |V| with V = E
    while e.nxt.origin != b and i <= 9999:
        i += 1
        e = e.twin.nxt
    if i > 9999:
        if verbose: print("INFO: Points (%i,%i) not connected" % (a.i, b.i))
    return e # edge e between vertices a and b


def isLeftOf(a, b, v, strict=False):
    if strict: return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) > 0
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) >= 0


def get_all_areas(verts):
    le = HDCEL.get_full_edge_list()
    chull = HDCEL.get_convex_hull(verts)

    for i in range(len(chull)):
        le.remove(getEdge(chull[i-1], chull[i]))

    areas = []

    while len(le)>1:
        oe = e = le.pop(0)
        area = []
        inflexes = []

        while e.nxt!=oe:
            area.append(e)
            if isLeftOf(e.prev.origin, e.origin, e.nxt.origin, strict=True): inflexes.append(e)

            if e in le: le.remove(e)
            e = e.nxt
        area.append(e)

        areas.append((oe, len(inflexes)==0, area, inflexes))
    return areas


def get_single_area(e):
    oe = e
    area = []
    inflexes = []

    while e.nxt!=oe:
        area.append(e)
        if isLeftOf(e.prev.origin, e.origin, e.nxt.origin, strict=True): inflexes.append(e)
        e = e.nxt
    area.append(e)

    return (oe, len(inflexes)==0, area, inflexes)


def run(verts):
    areas = get_all_areas(verts)

    while len(areas)>1:
        print(len(areas), end='')
        (e, convex, edges, inflexes) = areas.pop(0)
        if convex:
            continue
        else:
            #resolve_inflex(inflexes[0], edges, areas)
            #resolve_inflex(inflexes[0], get_single_area(inflexes[0])[2], areas)
            for i in inflexes:
                resolve_inflex(i, get_single_area(i)[2], areas)

def resolve_inflex(inflex, edges, areas):
    if not isLeftOf(inflex.prev.origin, inflex.origin, inflex.nxt.origin, strict=True):
        return

    ie = inflex
    e = bisect(ie, edges)

    #if e is None: return

    p1 = e.origin
    p2 = e.nxt.origin

    p1_valid = p2_valid = False
    p1_strong = p2_strong = False

    if ie.nxt.origin!=p1 and coll(ie.origin, p1, edges)[1] >= get_distance(ie.origin, p1):
        p1_valid = True
        if not isLeftOf(ie.prev.origin, ie.origin, p1) and not isLeftOf(ie.origin, ie.nxt.origin, p1): p1_strong = True

    if ie.prev.origin!=p2 and coll(ie.origin, p2, edges)[1] >= get_distance(ie.origin, p2):
        p2_valid = True
        if not isLeftOf(ie.prev.origin, ie.origin, p2) and not isLeftOf(ie.origin, ie.nxt.origin, p2): p2_strong = True

    if p1_strong:
        u = ie.origin.connect_to(p1)
        areas.append(get_single_area(u))
        areas.append(get_single_area(u.twin))
        return

    elif p2_strong:
        u = ie.origin.connect_to(p2)
        areas.append(get_single_area(u))
        areas.append(get_single_area(u.twin))
        return

    elif p1_valid and p2_valid and p1!=p2:
        u = ie.origin.connect_to(p1)
        u2 = ie.origin.connect_to(p2)
        areas.append(get_single_area(u))
        areas.append(get_single_area(u.twin))
        areas.append(get_single_area(u2))
        areas.append(get_single_area(u2.twin))
        return

    else:
        print("to the back of the queue!")
        return


def findIntersection(v1,v2,v3,v4):
    if v1==v3 or v1==v4: return v1
    if v2==v3 or v2==v4: return v2
    px= ( (v1.x()*v2.y()-v1.y()*v2.x())*(v3.x()-v4.x())-(v1.x()-v2.x())*(v3.x()*v4.y()-v3.y()*v4.x()) ) / ( (v1.x()-v2.x())*(v3.y()-v4.y())-(v1.y()-v2.y())*(v3.x()-v4.x()) )
    py= ( (v1.x()*v2.y()-v1.y()*v2.x())*(v3.y()-v4.y())-(v1.y()-v2.y())*(v3.x()*v4.y()-v3.y()*v4.x()) ) / ( (v1.x()-v2.x())*(v3.y()-v4.y())-(v1.y()-v2.y())*(v3.x()-v4.x()) )
    return Vertex(px, py)

def get_distance(v1, v2):
    return (v2.x() - v1.x())**2 + ( v2.y() - v1.y())**2

# May require strcit=True for colinear points?
def segment_intersect(l1, l2, g1, g2, strict=False):
    if len(set([l1,l2,g1,g2]))!=len([l1,l2,g1,g2]): return not strict
    return isLeftOf(l1, l2, g1) != isLeftOf(l1, l2, g2) and isLeftOf(g1, g2, l1) != isLeftOf(g1, g2, l2)

def coll(origin, dir, edges):
    dir = origin.add(HDCEL.Vertex((dir.x()-origin.x())*1000000, (dir.y()-origin.y())*1000000))
    min_dist = float('inf')
    min_e = None

    for e in edges:
        if segment_intersect(origin, dir, e.origin, e.nxt.origin, strict=True):
            collision_point = findIntersection(origin, dir, e.origin, e.nxt.origin)
            if  get_distance(origin, collision_point) < min_dist:
                min_dist = get_distance(origin, collision_point)
                min_e = e

    #assert(min_e is not None)
    if min_e is None:
        HVIS.drawSingleTEdge(origin, dir, color="r")
        for e in edges:
            HVIS.drawSingleEdge(e, color="k", width=1)
        HVIS.show()

    return min_e, min_dist

def bisect(inflex, edges, weird=False):
    g1 = inflex.to_vector().normalized().mul(-1)
    g2 = inflex.prev.to_vector().normalized()

    dir = g1.add(g2)
    dir = inflex.origin.add(dir)

    co, _ = coll(inflex.origin, dir, edges)

    return co
