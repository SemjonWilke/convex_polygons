import math
import sys
import HDCEL
from HDCEL import Vertex, angle
from random import seed
from random import randint
from enum import Enum
import numpy as np
from HJSON import readStartPoints
import HMERGE
import HCLEAN
import HFIX
import HVIS
from HDCEL import isLeftOf, isRightOf, are_colinear

vertices = []
hulls = []
verbose = False

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
    for i in range(len(starting_points)):
        h = Hull(starting_points[i])
        h.grow()
        if verbose: print("\r"+str(int(100*i/len(starting_points)))+"%", end='')
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
    if verbose: print("Done")

    # If edges are changed we need to call this again.
    HFIX.init()

    # Integrate Islands
    islands = HFIX.get_all_islands(vertices)
    if verbose: print(str(len(islands)) + " Islands detected.")
    for island in islands:
        HFIX.integrate_island(island, vertices)

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

    def __init__(self, startpoint=None):
        global vertices
        # Create starting point and vertex list
        if startpoint is None:
            self.origin = Vertex(explicit_x=randint(0,14000), explicit_y=randint(0,8000))
        else:
            self.origin = startpoint
        self.vertex_list = sortByDistance(vertices, self.origin)

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
        if not self.alive: return
        while self.current_index+1 < len(self.vertex_list):
            self.current_index += 1
            v = self.vertex_list[self.current_index]

            i, j = getVisibleBounds(v, self)
            i, j = self.ch_i(i), self.ch_i(j)

            if abs(j-i) > 1: continue
            if occluded(v, self.ch(i), self.ch(j), self): continue

            if j < i:
                self.convex_hull[i+1:len(self.convex_hull)] = [v]
                self.convex_hull[0:j] = []
            else:
                self.convex_hull[i+1:j] = [v]

            v.claimant = self
            self.radius = get_distance(self.origin, v)


        for i in range(len(self.convex_hull)):
            self.ch(i).connect_to(self.ch(i+1))

def center(a, b, c):
    """ Returns centroid (geometric center) of a triangle abc """
    avg_x = (a.x+b.x+c.x) / 3
    avg_y = (a.y+b.y+c.y) / 3
    return Vertex(explicit_x=avg_x, explicit_y=avg_y)

def isVisible(i, v, master, strict=True):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return isRightOf(master.ch(i), master.ch(i+1), v, strict)

def getSomeVisibleSegment(v, master):
    """ Returns index of some segment on the convex hull visible from v """
    min = 0
    max = len(master.convex_hull) - 1
    i = math.ceil((max - min) / 2)

    while max > min:
        i = min + math.ceil((max - min) / 2)
        if isVisible(i, v, master):
            return i

        if isLeftOf(center(master.ch(0), master.ch(1), master.ch(2)), master.ch(i), v):
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
    if (l1 in [l2, g1, g2] or l2 in [l1, g1, g2] or g1 in [l1, l2, g2] or g2 in [l1, l2, g1]):
        return strict
    return isLeftOf(l1, l2, g1) != isLeftOf(l1, l2, g2) and isLeftOf(g1, g2, l1) != isLeftOf(g1, g2, l2)

def circle_intersect(c1, r1, c2, r2):
    return get_distance(c1, c2) <= r1+r2

def occluded(v, left, right, target):
    for p in target.vertex_list[0:target.current_index]:
        if p!=v and p!=left and p!=right and PointInTriangle(p, v, right, left):
            return True

    d = get_distance(target.origin, v)
    relevant_hulls = [h for h in hulls if circle_intersect(h.origin, h.radius, target.origin, d)]
    for h in relevant_hulls:
        if h!=target:
            for i in range(len(h.convex_hull)):
                if segment_intersect(h.ch(i), h.ch(i+1), v, left, strict=False): return True
                if segment_intersect(h.ch(i), h.ch(i+1), v, right, strict=False): return True
    #print(len(relevant_hulls))
    return False

def m_sign (p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

def PointInTriangle (pt, v1, v2, v3):
    d1 = m_sign(pt, v1, v2);
    d2 = m_sign(pt, v2, v3);
    d3 = m_sign(pt, v3, v1);

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0);
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0);

    return not (has_neg and has_pos);
