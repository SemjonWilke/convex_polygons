
import HDCEL
from HDCEL import Vertex, isLeftOf_s, isRightOf_s, isRightOf_ns
import math
import heapq

verbose = False

local_full_edge_list = []
local_edge_list = []
areas = []
chull = []

def init(verts):
    global local_full_edge_list, local_edge_list, areas, chull
    local_full_edge_list, local_edge_list = HDCEL.get_both_edge_lists()
    chull = HDCEL.get_convex_hull(verts)
    if verbose: print("Acquiring all areas... ")
    areas = get_all_areas(verts)
    if verbose: print("Done")

def local_connect(a, b):
    global local_full_edge_list, local_edge_list
    e = a.connect_to(b)
    local_full_edge_list.append(e)
    local_full_edge_list.append(e.twin)
    local_edge_list.append(e)
    return e

def local_remove(e):
    global local_full_edge_list, local_edge_list
    local_full_edge_list.remove(e)
    local_full_edge_list.remove(e.twin)
    if e in local_edge_list: local_edge_list.remove(e)
    elif e.twin in local_edge_list: local_edge_list.remove(e.twin)
    e.remove()

def get_all_islands(verts):
    global local_full_edge_list, chull

    master = chull[0]
    HDCEL.mark_depth_first(master, mark=1) # 1 shall signify that this vertex is part of the main congolomerate

    islands = []
    le = [e for e in local_full_edge_list if e.origin.mark is None]
    all_island_edges = le.copy()
    while len(le)>0:
        e = le[0]
        islands.append(e)
        HDCEL.mark_depth_first(e.origin, mark=2) # 2 shall signify that this vertex is part of an isolated island
        le = [e for e in le if e.origin.mark is None]

    return islands, all_island_edges

def getEdge(a, b):
    e = a.incidentEdge
    while e.nxt.origin != b:
        e = e.twin.nxt
    return e # edge e between vertices a and b

def extract_closest(vlist, p):
    min_d = float('inf')
    min_v = None
    for v in vlist:
        if get_distance(v, p) < min_d:
            min_d = get_distance(v, p)
            min_v = v
    vlist.remove(v)
    return v

def get_all_areas(verts):
    global local_full_edge_list, chull
    le = local_full_edge_list.copy()

    for i in range(len(chull)):
        le.remove(getEdge(chull[i-1], chull[i]))

    areas = []
    while len(le)>1:
        oe = e = le.pop()
        while e.mark is not None:
            if len(le)<1: return areas
            oe = e = le.pop()

        if verbose: print("\r"+str(len(le)), end='')
        inflexes = []

        area = []
        while e.nxt!=oe:
            area.append(e)
            if e.mark is None:
                if isLeftOf_s(e.prev.origin, e.origin, e.nxt.origin): inflexes.append(e)
                e.mark = 1

            e = e.nxt
        area.append(e)

        areas.append((len(inflexes)==0, inflexes, oe, area))
    return areas

#non convex areas allowed
def contained_by_area_ncx(edges, v):
    le = [e for e in edges if (e.origin.y < v.y) != (e.nxt.origin.y < v.y)]
    le = [e for e in le if (e.origin.y < v.y and isRightOf_s(e.origin, e.nxt.origin, v)) or (e.nxt.origin.y < v.y and isRightOf_s(e.nxt.origin, e.origin, v))]
    if len(le)%2==0:
        return False
    return True

def integrate_island(edge_on_island, all_island_edges):
    global areas
    island_edges = get_single_area(edge_on_island)
    for i, (_, _, _, a) in enumerate(areas):
            if contained_by_area_ncx(a, edge_on_island.origin): #Found the surrounding area!
                for edge_on_island in island_edges:
                    for edge_on_area in a:
                        if edge_on_area.origin.mark==1 and can_place_edge2(edge_on_island.origin, edge_on_area.origin, all_island_edges) and can_place_edge2(edge_on_island.origin, edge_on_area.origin, a):
                            HDCEL.mark_depth_first(edge_on_island.origin, mark=1) # Mark this island as mainland
                            new_e = local_connect(edge_on_island.origin, edge_on_area.origin)
                            all_island_edges.append(new_e)
                            areas.append(get_single_area_tuple_with_edges(new_e))
                            areas.append(get_single_area_tuple_with_edges(new_e.twin))
                            del areas[i]
                            return
    if verbose: print("ERR: Could not integrate island.")

# Use this sparingly as it runs poorly
def can_place_edge(a, b, allow_existing=True):
    global local_edge_list
    if not allow_existing and b in [e.nxt.origin for e in a.get_connected_edges()]:
        return False
    for e in local_edge_list:
        if segment_intersect(e.origin, e.nxt.origin, a, b, strict=True):
            return False
    return True

def can_place_edge2(a, b, elist):
    for e in elist:
        if segment_intersect(e.origin, e.nxt.origin, a, b, strict=True):
            return False
    return True

def point_on_edge(p, e):
    if isLeftOf_s(e.origin, e.nxt.origin, p) or isRightOf_s(e.origin, e.nxt.origin, p):
        return False
    # p and e are colinear.
    em = get_distance(e.origin, e.nxt.origin)
    return get_distance(e.origin, p) <= em and get_distance(e.nxt.origin, p) <= em

def get_edge_below_point(p):
    global local_edge_list
    for e in local_edge_list:
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
            tmp1, tmp2 = e.origin, e.nxt.origin
            local_remove(e)
            local_connect(tmp1, p)
            local_connect(tmp2, p)
        # Stray point is inside of an area:
        else:
            a = get_surrounding_area(p)
            integrate_into_area(p, a)

def integrate_into_area(p, edgelist):
    last_edge = local_connect(p, edgelist[0].origin)
    for e in edgelist[1:]:
        if HDCEL.angle(last_edge, e.origin) >= 180:
            last_edge = local_connect(p, e.origin)

def get_single_area_tuple(e):
    oe = e
    inflexes = []

    """TODO this is NOT a fix, it simply aborts on infinite loops!"""
    i = 0
    while e.nxt!=oe:
        i+=1
        if i > len(local_full_edge_list):
            print("abort (0) due to inf loop")
            exit(600)
        """TODO"""
        if isLeftOf_s(e.prev.origin, e.origin, e.nxt.origin): inflexes.append(e)
        e = e.nxt

    return (len(inflexes)==0, inflexes, oe, -1)

def get_single_area_tuple_with_edges(e):
    oe = e
    inflexes = []

    area = []
    """TODO this is NOT a fix, it simply aborts on infinite loops!"""
    i = 0
    while e.nxt!=oe:
        i+=1
        if i > len(local_full_edge_list):
            print("abort (1) due to inf loop")
            exit(600)
        """TODO"""
        area.append(e)
        if isLeftOf_s(e.prev.origin, e.origin, e.nxt.origin): inflexes.append(e)
        e = e.nxt
    area.append(e)

    return (len(inflexes)==0, inflexes, oe, area)

def get_single_area(e):
    oe = e
    area = []
    while e.nxt!=oe:
        area.append(e)
        e = e.nxt
    area.append(e)
    return area

def get_surrounding_area(p):
    global local_full_edge_list
    le = local_full_edge_list
    #Performance: First check for the closest edges:
    h = heapq.nsmallest(40, le, key=lambda x: get_distance(x.origin, p))
    for e in h:
        a = get_single_area(e)
        if point_in_area(a, p): return a
    for e in le:
        a = get_single_area(e)
        if point_in_area(a, p): return a
    return None

def point_in_area(edgelist, p): #Note: only works for convex areas.
    for e in edgelist:
        if isLeftOf_s(e.origin, e.nxt.origin, p):
            return False
    return True


def run(verts):
    deadlock_limit = 2*len(verts)
    while len(areas)>1:
        if verbose: print("\r"+str(len(areas)), end='')
        (convex, inflexes, edge, _) = areas.pop(0) # NOTE: at this point in the ptorgram there is no guarantee that the fourth element of the area tuple is valid.
        if convex:
            continue
        else:
            if len(areas)>deadlock_limit:
                if verbose: print("INFO: Deadlock during resolve pass.")
                for e in get_single_area(inflexes[0]):
                    if e.origin != inflexes[0].origin and can_place_edge(e.origin, inflexes[0].origin, allow_existing=False):
                        new_e = local_connect(e.origin, inflexes[0].origin)
                        areas.append(get_single_area_tuple(new_e))
                        areas.append(get_single_area_tuple(new_e.twin))
                        deadlock_limit += len(verts)
                        break
            for i in inflexes:
                resolve_inflex(i, get_single_area(i), areas)

def resolve_inflex(inflex, edges, areas):
    if isRightOf_ns(inflex.prev.origin, inflex.origin, inflex.nxt.origin): return # This is not an inflex -> dont care

    ie = inflex
    e = bisect(ie, edges)

    if e is None:
        if verbose: print("ERR: Bisection Failed!")
        return

    p1 = e.origin
    p2 = e.nxt.origin

    p1_valid = p2_valid = False
    p1_strong = p2_strong = False

    if ie.nxt.origin!=p1 and coll(ie.origin, p1, edges)[1] >= get_distance(ie.origin, p1):
        p1_valid = True
        if isRightOf_ns(ie.prev.origin, ie.origin, p1) and isRightOf_ns(ie.origin, ie.nxt.origin, p1): p1_strong = True

    if ie.prev.origin!=p2 and coll(ie.origin, p2, edges)[1] >= get_distance(ie.origin, p2):
        p2_valid = True
        if isRightOf_ns(ie.prev.origin, ie.origin, p2) and isRightOf_ns(ie.origin, ie.nxt.origin, p2): p2_strong = True

    if p1_strong:
        u = local_connect(ie.origin, p1)
        areas.append(get_single_area_tuple(u))
        areas.append(get_single_area_tuple(u.twin))
        return

    elif p2_strong:
        u = local_connect(ie.origin, p2)
        areas.append(get_single_area_tuple(u))
        areas.append(get_single_area_tuple(u.twin))
        return

    elif p1_valid and p2_valid and p1!=p2:
        u = local_connect(ie.origin, p1)
        u2 = local_connect(ie.origin, p2)
        areas.append(get_single_area_tuple(u))
        areas.append(get_single_area_tuple(u.twin))
        areas.append(get_single_area_tuple(u2))
        areas.append(get_single_area_tuple(u2.twin))
        return

    else:
        areas.append(get_single_area_tuple(inflex)) #Theoretically not necessary, but doesnt work without it (?)
        return


def findIntersection(v1,v2,v3,v4):
    if v1==v3 or v1==v4: return v1
    if v2==v3 or v2==v4: return v2
    px= ( (v1.x*v2.y-v1.y*v2.x)*(v3.x-v4.x)-(v1.x-v2.x)*(v3.x*v4.y-v3.y*v4.x) ) / ( (v1.x-v2.x)*(v3.y-v4.y)-(v1.y-v2.y)*(v3.x-v4.x) )
    py= ( (v1.x*v2.y-v1.y*v2.x)*(v3.y-v4.y)-(v1.y-v2.y)*(v3.x*v4.y-v3.y*v4.x) ) / ( (v1.x-v2.x)*(v3.y-v4.y)-(v1.y-v2.y)*(v3.x-v4.x) )
    return Vertex(px, py)

def get_distance(v1, v2):
    return (v2.x - v1.x)**2 + ( v2.y - v1.y)**2

# May require strcit=True for colinear points?
def segment_intersect(l1, l2, g1, g2, strict=False):
    if l1==l2 or l1==g1 or l1==g2 or l2==g1 or l2==g2 or g1==g2:
        return not strict
    return isLeftOf_s(l1, l2, g1) != isLeftOf_s(l1, l2, g2) and isLeftOf_s(g1, g2, l1) != isLeftOf_s(g1, g2, l2)

def coll(origin, dir, edges, mul=2000000):
    dir = HDCEL.Vertex(dir.x-origin.x, dir.y-origin.y)
    dir = dir.mul(mul) #NOTE: Normalizing dir before multiplying breaks the program and I dont know why.
    dir = origin.add(dir)

    min_dist = float('inf')
    min_e = None

    for e in edges:
        if segment_intersect(origin, dir, e.origin, e.nxt.origin, strict=True):
            collision_point = findIntersection(origin, dir, e.origin, e.nxt.origin)
            if  get_distance(origin, collision_point) < min_dist:
                min_dist = get_distance(origin, collision_point)
                min_e = e

    # We dont want to return actual floats if they are not infinite, as this will cause floating point issues.
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

    if co is None:
        co, _ = coll(inflex.origin, dir, edges, mul=2000000000)

    return co
