import HDCEL
from HDCEL import Vertex, isLeftOf, isRightOf
import HVIS
import HCLEAN
import math

verbose = False

def get_all_islands(verts):
    master = HDCEL.get_convex_hull(verts)[0]
    HDCEL.mark_depth_first(master, mark=1) # 1 shall signify that this vertex is part of the main congolomerate

    islands = []
    le = [e for e in HDCEL.get_full_edge_list() if e.origin.mark is None]
    while len(le)>0:
        e = le[0]
        islands.append(e)
        HDCEL.mark_depth_first(e.origin, mark=2) # 2 shall signify that this vertex is part of an isolated island
        le = [e for e in le if e.origin.mark is None]
    return islands


def getEdge(a, b):
    e = a.incidentEdge
    i = 0 # guard to prevent endless loop, i is at most |V| with V = E
    while e.nxt.origin != b and i <= 9999:
        i += 1
        e = e.twin.nxt
    if i > 9999:
        if verbose: print("INFO: Points (%i,%i) not connected" % (a.i, b.i))
    return e # edge e between vertices a and b

def sortByDistance(vlist, p):
    """ Sorts a list of vertices by euclidean distance towards a reference vertex p """
    rlist = vlist.copy()
    rlist.sort(key=lambda x: get_distance(x, p))
    return rlist


def get_all_areas(verts):
    le = HDCEL.get_full_edge_list()
    chull = HDCEL.get_convex_hull(verts)

    for i in range(len(chull)):
        le.remove(getEdge(chull[i-1], chull[i]))

    areas = []

    while len(le)>1:
        if verbose: print("\r"+str(len(le)), end='')
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

def integrate_island(edge_on_island, vertices):
    island_edges = get_single_area(edge_on_island)[2]

    for edge_on_island in island_edges:
        verts = sortByDistance(vertices, edge_on_island.origin) # we'll just sort by distance to this point why not
        for v in verts:
            if v.claimant is not None and v.mark==1:
                if can_place_edge(edge_on_island.origin, v):
                    HDCEL.mark_depth_first(edge_on_island.origin, mark=1) # Mark this island as mainland
                    edge_on_island.origin.connect_to(v)
                    if verbose: print("Island integrated.")
                    return
    if verbose: print("ERR: Could not integrate island.")


# Use this sparingly as it runs poorly
def can_place_edge(a, b):
    edges = HDCEL.get_edge_list()
    for i in range(len(edges)):
        if segment_intersect(edges[i].origin, edges[i].nxt.origin, a, b, strict=True):
            return False
    return True

def point_on_edge(p, e):
    if isLeftOf(e.origin, e.nxt.origin, p, strict=True) or isRightOf(e.origin, e.nxt.origin, p, strict=True):
        return False
    # p and e are colinear.
    em = get_distance(e.origin, e.nxt.origin)
    return get_distance(e.origin, p) <= em and get_distance(e.nxt.origin, p) <= em

def get_edge_below_point(p):
    edges = HDCEL.get_edge_list()
    for e in edges:
        if point_on_edge(p, e): return e
    return None

def integrate(stray_points):
    if verbose: print(str(len(stray_points))+" stray points detected.")
    for i in range(len(stray_points)):
        if verbose: print("\r"+str(len(stray_points)-i), end="")
        p = stray_points[i]

        # Stray point is on top of an edge:
        e = get_edge_below_point(p)
        if e is not None:
            e.origin.connect_to(p)
            e.nxt.origin.connect_to(p)
            e.remove()
        # Stray point is inside of an area:
        else:
            a = get_surrounding_area(p)
            integrate_into_area(p, a)

def integrate_into_area(p, edgelist):
    last_edge = p.connect_to(edgelist[0].origin)
    for e in edgelist[1:]:
        if HDCEL.angle(last_edge, e.origin) >= 180:
            last_edge = p.connect_to(e.origin)

def get_single_area(e):
    oe = e
    area = []
    inflexes = []

    c = 0
    while e.nxt!=oe:
        c += 1
        if c>2000:
            if verbose: print("Endless loop")
            return

        area.append(e)
        if isLeftOf(e.prev.origin, e.origin, e.nxt.origin, strict=True): inflexes.append(e)
        e = e.nxt
    area.append(e)

    return (oe, len(inflexes)==0, area, inflexes)

def get_surrounding_area(p):
    le = HDCEL.get_full_edge_list()
    #TODO: sort edges by distance to point?
    for e in le:
        a = get_single_area(e)[2]
        if point_in_area(a, p): return a
    return None

def point_in_area(edgelist, p): #Note: only works for convex areas.
    for e in edgelist:
        if isLeftOf(e.origin, e.nxt.origin, p, strict=True):
            return False
    return True


def run(verts):
    if verbose: print("Acquiring all areas... ", end="")
    areas = get_all_areas(verts)
    if verbose: print("Done")

    while len(areas)>1:
        if verbose: print("\r"+str(len(areas)), end='')
        (e, convex, edges, inflexes) = areas.pop(0)
        if convex:
            continue
        else:
            for i in inflexes:
                resolve_inflex(i, get_single_area(i)[2], areas)

def resolve_inflex(inflex, edges, areas):
    if isRightOf(inflex.prev.origin, inflex.origin, inflex.nxt.origin, strict=False): return # This is not an inflex -> dont care

    ie = inflex
    e = bisect(ie, edges)

    if e is None:
        if verbose: print("ERR: Bisection Failed!")
        return

    p1 = e.origin
    p2 = e.nxt.origin

    p1_valid = p2_valid = False
    p1_strong = p2_strong = False

    # TODO: Are there cases were the "isRightOf"s *should* be strict?
    if ie.nxt.origin!=p1 and coll(ie.origin, p1, edges)[1] >= get_distance(ie.origin, p1):
        p1_valid = True
        if isRightOf(ie.prev.origin, ie.origin, p1, strict=False) and isRightOf(ie.origin, ie.nxt.origin, p1, strict=False): p1_strong = True

    if ie.prev.origin!=p2 and coll(ie.origin, p2, edges)[1] >= get_distance(ie.origin, p2):
        p2_valid = True
        if isRightOf(ie.prev.origin, ie.origin, p2, strict=False) and isRightOf(ie.origin, ie.nxt.origin, p2, strict=False): p2_strong = True

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
    return isLeftOf(l1, l2, g1, strict=True) != isLeftOf(l1, l2, g2, strict=True) and isLeftOf(g1, g2, l1, strict=True) != isLeftOf(g1, g2, l2, strict=True)

def coll(origin, dir, edges):
    dir = HDCEL.Vertex(dir.x()-origin.x(), dir.y()-origin.y())
    dir = dir.mul(2000000) #NOTE: Normalizing dir before multiplying breaks the program and I dont know why.
    dir = origin.add(dir)

    min_dist = float('inf')
    min_e = None

    for e in edges:
        if segment_intersect(origin, dir, e.origin, e.nxt.origin, strict=True):
            collision_point = findIntersection(origin, dir, e.origin, e.nxt.origin)
            if  get_distance(origin, collision_point) < min_dist:
                min_dist = get_distance(origin, collision_point)
                min_e = e

    #assert(min_e is not None)
    #if min_e is None:
    #    HVIS.drawSingleTEdge(origin, dir, color="r")
    #    for e in edges:
    #        HVIS.drawSingleEdge(e, color="k", width=1)
    #    HVIS.show()

    if min_dist < float('inf'):
        return min_e, math.ceil(min_dist)
    else:
        return min_e, min_dist

def bisect(inflex, edges):
    g1 = inflex.to_vector().normalized().mul(-1)
    g2 = inflex.prev.to_vector().normalized()

    dir = g1.add(g2)
    dir = inflex.origin.add(dir)

    co, _ = coll(inflex.origin, dir, edges)

    return co
