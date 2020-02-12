import math
import sys
import HDCEL
from HDCEL import Vertex, angle
from random import seed
from random import randint
from enum import Enum
import numpy as np
from HJSON import readStartPoints
import HCLEAN
import HFIX
from HDCEL import are_colinear, isLeftOf_s, isRightOf_s, isLeftOf_ns, isRightOf_ns
import threading

vertices = []
hulls = []
verbose = False
vlists = []

def sorting_thread(spoints):
    global vlists
    for p in spoints:
        vlists.append(sortByDistance(vertices, p))

def run(_vertices, _filename, _verbose, _explicit):
    global vertices, verbose
    vertices = _vertices
    verbose = _verbose

    l = readStartPoints(_filename)
    if len(l) == 0 or _explicit == 0:
        if verbose: print("Using random startpoints")
        starting_points = [Vertex(explicit_x=randint(0,14000), explicit_y=randint(0,8000)) for i in range(4)]
    else:
        sp_len = int(len(l) * min((float(_explicit)/100.0), 1.0))
        starting_points = [Vertex(explicit_x=l[i][0], explicit_y=l[i][1]) for i in range(sp_len)]

    # First pass
    if verbose: print("First pass...")
    sortingThread = threading.Thread(target=sorting_thread, args=(starting_points,))
    sortingThread.start()
    for i in range(len(starting_points)):
        while len(vlists)<i+1:
            continue
        h = Hull(starting_points[i], vlists[i])
        h.grow()
        vlists[i] = []
        if verbose: print("\r"+str(int(100*i/len(starting_points)))+"%", end='')
    sortingThread.join()
    if verbose: print("\rDone")

    # Second pass
    if verbose: print("Second pass...")
    for i in range(len(vertices)):
        if vertices[i].claimant is None:
            h = Hull(vertices[i])
            h.grow()
        if verbose: print("\r"+str(int(100*i/len(vertices)))+"%", end='')
    if verbose: print("\rDone")

    # Convex hull
    if verbose: print("Outer hull...")
    HDCEL.form_convex_hull(vertices)

    # If edges are changed we need to call this again.
    HFIX.init(vertices)

    # Integrate Islands
    islands, all_island_edges = HFIX.get_all_islands(vertices)
    if verbose: print(str(len(islands)) + " Islands detected.")
    for island in islands:
        HFIX.integrate_island(island, all_island_edges)

    # Resolve inflexes
    if verbose: print("Resolve pass...")
    HFIX.run(vertices)

    # Integrate stray points
    if verbose: print("Integrating stray points")
    HFIX.integrate([v for v in vertices if v.incidentEdge is None])

    # Clean
    if verbose: print("Final Cleaning pass")
    HCLEAN.clean_edges()

    #HCLEAN.check_cross()


class Hull:
    origin = None
    vertex_list = None
    current_index = -1
    convex_hull = []
    alive = False
    radius = float('inf')

    def ch(self, i):
        return self.convex_hull[i % len(self.convex_hull)]

    def ch_i(self, i):
        return i % len(self.convex_hull)

    def __init__(self, startpoint, vlist=None):
        global vertices
        # Create starting point and vertex list
        self.origin = startpoint
        if vlist is None:
            self.vertex_list = sortByDistance(vertices, self.origin)
        else:
            self.vertex_list = vlist

        # First check if we can at least make a triangle at this location. If we can't we may as well toss this iterator
        if self.vertex_list[0].claimant is not None and self.vertex_list[0].claimant == self.vertex_list[1].claimant == self.vertex_list[2].claimant: return

        # Three colinear points do not make a triangle.
        if are_colinear(self.vertex_list[0], self.vertex_list[1], self.vertex_list[2]): return

        self.convex_hull = HDCEL.get_triangle(self.vertex_list[0], self.vertex_list[1], self.vertex_list[2])
        self.radius = max([get_distance(self.origin, self.vertex_list[0]), get_distance(self.origin, self.vertex_list[1]), get_distance(self.origin, self.vertex_list[2])])

        for h in hulls:
            if circle_intersect(self.origin, self.radius, h.origin, h.radius):
                for i in range(len(h.convex_hull)):
                    if segment_intersect(h.ch(i), h.ch(i+1), self.convex_hull[0], self.convex_hull[1], strict=False): return
                    if segment_intersect(h.ch(i), h.ch(i+1), self.convex_hull[1], self.convex_hull[2], strict=False): return
                    if segment_intersect(h.ch(i), h.ch(i+1), self.convex_hull[2], self.convex_hull[0], strict=False): return

        self.vertex_list[0].claimant = self
        self.vertex_list[1].claimant = self
        self.vertex_list[2].claimant = self
        self.current_index = 2
        self.alive = True

        hulls.append(self)

    def grow(self):
        failed = 0
        if not self.alive: return
        while self.current_index+1 < len(self.vertex_list) and failed<100:
            self.current_index += 1
            v = self.vertex_list[self.current_index]

            i, j = getVisibleBounds(v, self)
            i, j = self.ch_i(i), self.ch_i(j)

            failed += 1
            if abs(j-i) > 1: continue
            if occluded(v, self.ch(i), self.ch(j), self): continue
            failed = 0

            if j < i:
                self.convex_hull[i+1:len(self.convex_hull)] = [v]
                self.convex_hull[0:j] = []
            else:
                self.convex_hull[i+1:j] = [v]

            v.claimant = self
            self.radius = get_distance(self.origin, v)


        for i in range(len(self.convex_hull)):
            self.ch(i).connect_to(self.ch(i+1))

        self.vertex_list = []

def center(a, b, c):
    """ Returns centroid (geometric center) of a triangle abc """
    avg_x = (a.x+b.x+c.x) / 3
    avg_y = (a.y+b.y+c.y) / 3
    return Vertex(explicit_x=avg_x, explicit_y=avg_y)

def isVisible(i, v, master):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return isRightOf_s(master.ch(i), master.ch(i+1), v)

def getSomeVisibleSegment(v, master):
    """ Returns index of some segment on the convex hull visible from v """
    min = 0
    max = len(master.convex_hull) - 1
    i = math.ceil((max - min) / 2)

    while max > min:
        i = min + math.ceil((max - min) / 2)
        if isVisible(i, v, master):
            return i

        if isLeftOf_ns(center(master.ch(0), master.ch(1), master.ch(2)), master.ch(i), v):
            min = i + 1
        else:
            max = i - 1

    if isVisible(max + 1, v, master):
        return max + 1
    if isVisible(max - 1, v, master):
        return max - 1
    if not isVisible(max, v, master):
        #print("ERROR: NON-VISIBLE-EDGE! Falling back to iterative result.")
        for i in range(len(master.convex_hull)):
            if isVisible(i, v, master):
                return i
    return max

def getVisibleBounds(v, master):
    """ Returns the index of vertex v on the convex hull furthest 'to the left' visible from v """
    left = right = getSomeVisibleSegment(v, master)
    while isVisible(left - 1, v, master):
        left -= 1
    while isVisible(right + 1, v, master):
        right += 1
    return left, right+1

def get_distance(v1, v2):
    """ Returns euclidean distance between two points """
    return (v2.x - v1.x)**2 + ( v2.y - v1.y)**2

def sortByDistance(vlist, p):
    """ Sorts a list of vertices by euclidean distance towards a reference vertex p """
    rlist = vlist.copy()
    rlist.sort(key=lambda x: get_distance(x, p))
    return rlist

def segment_intersect(l1, l2, g1, g2, strict=True):
    if l1==l2 or l1==g1 or l1==g2 or l2==g1 or l2==g2 or g1==g2:
        return strict
    return isLeftOf_ns(l1, l2, g1) != isLeftOf_ns(l1, l2, g2) and isLeftOf_ns(g1, g2, l1) != isLeftOf_ns(g1, g2, l2)

def circle_intersect(c1, r1, c2, r2):
    return get_distance(c1, c2) <= (math.sqrt(r1)+math.sqrt(r2))**2

def occluded(v, left, right, target):
    for p in target.vertex_list[0:target.current_index]:
        if p!=v and p!=left and p!=right and PointInTriangle(p, v, left, right):
            return True

    d = get_distance(target.origin, v)
    relevant_hulls = [h for h in hulls if circle_intersect(h.origin, h.radius, target.origin, d)]
    for h in relevant_hulls:
        if h!=target:
            for i in range(len(h.convex_hull)):
                if segment_intersect(h.ch(i), h.ch(i+1), v, left, strict=False): return True
                if segment_intersect(h.ch(i), h.ch(i+1), v, right, strict=False): return True
    return False

def PointInTriangle (pt, v1, v2, v3):
    return isRightOf_ns(v1, v2, pt) and isRightOf_ns(v2, v3, pt) and isRightOf_ns(v3, v1, pt)