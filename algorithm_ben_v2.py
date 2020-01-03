import math
import sys
import HDCEL
from HDCEL import Vertex, angle
from random import seed
from random import randint
from enum import Enum
import numpy as np
from HSIDES import *
from HEARTRIM import earTrimArea
from HJSON import readStartPoints

seed(98765432)
all_iterators = []
active_iterators = []
vertices = []
verbose = False

def run(_vertices, _startpoints, _verbose):
    global vertices, verbose
    vertices = _vertices
    verbose = _verbose

    if verbose: print("Bens Algorithm v2")
    vertices = [Vertex(index=i) for i in range(len(vertices))]

    startpoints = []
    if _startpoints is None:
        if verbose: print("Using random startpoints")
        starting_points = [Vertex(explicit_x=randint(0,14000), explicit_y=randint(0,8000)) for i in range(4)]
    else:
        if verbose: print("Startpoints: " + _startpoints)
        l = readStartPoints(_startpoints)
        starting_points = [Vertex(explicit_x=l[i][0], explicit_y=l[i][1]) for i in range(len(l))]

    for p in starting_points:
        Iterator(p)

    while(cycle()): continue

def  center(a, b, c):
    """ Returns centroid (geometric center) of a triangle abc """
    avg_x = (a.x()+b.x()+c.x()) / 3
    avg_y = (a.y()+b.y()+c.y()) / 3
    return Vertex(explicit_x=avg_x, explicit_y=avg_y)

def isLeftOf(a, b, v, strict=False):
    """ (Orient.test) Returns true if v is to the left of a line from a to b. Otherwise false. """
    if strict: return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) > 0
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) >= 0

def isRightOf(a, b, v, strict=False):
    """ (Orient.test) Returns true if v is to the right of a line from a to b. Otherwise false. """
    if strict: return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) < 0
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) <= 0

def isLeftOfEdge(e, v):
    """ Same as above but takes an Edge as parameter instead of two points """
    return isLeftOf(e.origin, e.nxt.origin, v)

def isVisible(i, v, master, strict=True):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return not isLeftOf(master.ch(i), master.ch(i+1), v, strict)

def isVisibleEdge(e, v, strict=True):
    """ Returns true if the i'th segment of the convex_hull is visible from v """
    return not isLeftOf(e.origin, e.nxt.origin, v, strict)

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
    return (v2.x() - v1.x())**2 + ( v2.y() - v1.y())**2

def sortByDistance(vlist, p):
    """ Sorts a list of vertices by euclidean distance towards a reference vertex p """
    rlist = vlist.copy()
    rlist.sort(key=lambda x: get_distance(x, p))
    return rlist

def sortByDistanceToHull(vlist, hull):
    """ Sorts a list of vertices by euclidean distance towards a reference vertex p """
    rlist = vlist.copy()
    rlist.sort(key=lambda x: hull_point_distance(hull, x))
    return rlist

def getEdge(a, b):
    e = a.incidentEdge
    i = 0
    while e.nxt.origin != b:
        i += 1
        if e.twin.nxt==a.incidentEdge:
            break
        e = e.twin.nxt
    if e.nxt.origin != b:
        return None
    return e # edge e between vertices a and b

def segment_line_intersect(s1, s2, l1, l2):
    return isLeftOf(l1, l2, s1) != isLeftOf(l1, l2, s2)

def segment_intersect(l1, l2, g1, g2):
    if l1 in [l2, g1, g2] or l2 in [l1, g1, g2] or g1 in [l1, l2, g2] or g2 in [l1, l2, g1]:
        return False
    return isLeftOf(l1, l2, g1) != isLeftOf(l1, l2, g2) and isLeftOf(g1, g2, l1) != isLeftOf(g1, g2, l2)

def getCHIndex(p, master):
    for i in range(len(master.convex_hull)):
        if master.ch(i) == p: return i
    return None

# TODO: What if another hull intersects the triangle but doesnt have points in it?
def occluded(v, left, right, target):
    for it in active_iterators:
        if it!=target:
            for p in it.convex_hull:
                if PointInTriangle(p, v, right, left) and p!=v and p!=left and p!=right:
                    return True
            if it.intersects(v, left) or it.intersects(v, right):
                return True
    return False

def m_sign (p1, p2, p3):
    return (p1.x() - p3.x()) * (p2.y() - p3.y()) - (p2.x() - p3.x()) * (p1.y() - p3.y())

def PointInTriangle (pt, v1, v2, v3):
    d1 = m_sign(pt, v1, v2);
    d2 = m_sign(pt, v2, v3);
    d3 = m_sign(pt, v3, v1);

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0);
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0);

    return not (has_neg and has_pos);

def PointInRectangle(pt, v1, v2, v3, v4):
    if pt==v1 or pt==v2 or pt==v3 or pt==v4:
        return False
    # v3 and v4 are on opposite sides of v1_v2
    if isLeftOf(v1, v2, v3) != isLeftOf(v1, v2, v4):
        return PointInTriangle(pt, v1, v2, v3) or PointInTriangle(pt, v1, v2, v4)
    elif isLeftOf(v1, v3, v2) != isLeftOf(v1, v3, v4):
        return PointInTriangle(pt, v1, v3, v2) or PointInTriangle(pt, v1, v3, v4)
    else:
        return PointInTriangle(pt, v1, v4, v2) or PointInTriangle(pt, v1, v4, v3)

def split_by_line(pointset, l1, l2):
    left = []
    right = []
    for p in pointset:
        if isLeftOf(l1, l2, p):
            left.append(p)
        else:
            right.append(p)
    return left, right

def destroy_iterator(it):
    for v in vertices:
        if v.claimant==it:
            v.clear()
    it.alive = False
    if it in active_iterators: active_iterators.remove(it)

class It_Response (Enum):
    DEAD = 0
    UNABLE_SKIPPED = 1
    ABLE_REFUSED = 2
    ABLE_COMPLETED = 3
    ERROR = 4

class Iterator:
    origin = None
    vertex_list = None
    current_index = -1
    tolerance = 0.01
    convex_hull = []
    initialized = False
    alive = False

    def ch(self, i):
        return self.convex_hull[i % len(self.convex_hull)]

    def ch_i(self, i):
        return i % len(self.convex_hull)

    def completion(self):
        return self.current_index / len(self.vertex_list)

    def intersects(self, l1, l2, isSegment=True):
        for i in range(len(self.convex_hull)):
            if isSegment and segment_intersect(self.ch(i), self.ch(i+1), l1, l2):
                return True
            elif not isSegment and segment_line_intersect(self.ch(i), self.ch(i+1), l1, l2):
                return True
        return False

    def contains(self, point):
        if point in self.convex_hull:
            return True
        for i in range(len(self.convex_hull)):
            if not isLeftOf(self.ch(i), self.ch(i+1), point):
                return True
        return False

    def fix_hull(self, point_on_hull=None, thorough=False):
        # Find a single point that is still on the convex hull:
        p = point_on_hull
        if p is None:
            for p in self.convex_hull:
                if p.claimant==self: break

        # TODO: if p is still None => No points of this poor fella left => self-destruct
        if p is None:
            destroy_iterator(self)
            return

        e = p.get_convex_incidentEdge()
        starting_e = e
        if e is None:
            destroy_iterator(self)
            return

        new_hull = []
        while 1:
            new_hull.append(e.origin)
            e = e.nxt
            if e == starting_e: break

        # TODO: if len(new)<3: Less than a triangle remains => self-destruct
        if len(new_hull)<3: # Leave at least a triangle behing
            destroy_iterator(self)
            return

        self.convex_hull = new_hull

        i = 0
        while i<len(self.convex_hull):
            while not isLeftOf(self.ch(i-1), self.ch(i), self.ch(i+1)):
                del self.convex_hull[self.ch_i(i)]
                i-=1
            i+=1

        if len(new_hull)<3: # Leave at least a triangle behing
            destroy_iterator(self)
            return

        for i in range(len(self.convex_hull)):
            self.ch(i).claimant = self
            self.ch(i).on_hull = True
            if getEdge(self.ch(i), self.ch(i+1)) is None:
                ne = self.ch(i).connect_to(self.ch(i+1))
                earTrimArea(ne.twin)

        if thorough:
            for v in self.convex_hull[0:self.current_index+1]:
                if not self.contains(v):
                    v.clear()


    def merge(self, other, debug=False):
        if other==self: return
        o_right = 0
        s_right = 0

        while 1:
            # if s_right is visible from other but s_right-1 isnt => s_right correct
            if not (isVisible(self.ch_i(s_right), other.ch(o_right), self) and not isVisible(self.ch_i(s_right-1), other.ch(o_right), self)):
                s_right += 1
            # if o_right-1 is visible from self but o_right isnt => o_right correct
            elif not (isVisible(other.ch_i(o_right-1), self.ch(s_right), other) and not isVisible(other.ch_i(o_right), self.ch(s_right), other)):
                o_right += 1
            else:
                break

        o_left = 0
        s_left = 0

        while 1:
            # if o_left can see the previous one but not the next one => s_left is correct
            if not (isVisible(self.ch_i(s_left-1), other.ch(o_left), self) and not isVisible(self.ch_i(s_left), other.ch(o_left), self)):
                s_left += 1
            # if s_left can see this one but not the previous one => o_left is correct
            elif not (isVisible(other.ch_i(o_left), self.ch(s_left), other) and not isVisible(other.ch_i(o_left-1), self.ch(s_left), other)):
                o_left += 1
            else:
                break

        slv = self.ch(s_left)
        srv = self.ch(s_right)
        olv = other.ch(o_left)
        orv = other.ch(o_right)

        dom = [
            v for v in vertices \
            if PointInRectangle(v, slv, olv, srv, orv) \
            and v.claimant != self and v.claimant != other
        ]

        iterators_to_fix = []
        for v in dom:
            if v.claimant is not None and v.claimant!=self and v.claimant!=other: iterators_to_fix.append(v.claimant)
            v.clear()
        for it in iterators_to_fix:
            it.fix_hull(thorough=True)


        inter, nrm = intermediate_point(self, other)
        # Make sure we are to the right of nrm, so that split_by_line works:
        if isLeftOf(inter, nrm, self.ch(0), True):
            inter, nrm = nrm, inter

        other_dom, self_dom = split_by_line(dom, inter, nrm)

        self_dom = sortByDistanceToHull(self_dom, self)
        other_dom = sortByDistanceToHull(other_dom, other)

        for v in self_dom:
            if self.iterate(override=v)==It_Response.UNABLE_SKIPPED:
                print("ERR: Partition invalid.")
        for v in other_dom:
            if other.iterate(override=v)==It_Response.UNABLE_SKIPPED:
                print("ERR: Partition invalid.")

        # Note to self: The indeces of s_left and s_right etc. have shifted due to changes in the convex hull and are no longer valid here
        #   We retrieve them here using slv, srv, olv and orv:
        s_left = getCHIndex(slv, self)
        s_right = getCHIndex(srv, self)
        o_left = getCHIndex(olv, other)
        o_right = getCHIndex(orv, other)
        s_it = s_left
        o_it = o_left

        #if debug: return

        s = [self.ch(s_left)]
        i = s_left - 1
        while self.ch_i(s_right)!=self.ch_i(i):
            s.append(self.ch(i))
            i-=1
        s.append(self.ch(s_right))

        o = [other.ch(o_left)]
        i = o_left + 1
        while other.ch_i(o_right)!=other.ch_i(i):
            o.append(other.ch(i))
            i+=1
        o.append(other.ch(o_right))

        i, j = 0, 0
        s[i].connect_to(o[j])

        if self.ch_i(s_left)==self.ch_i(s_right) and len(o)<=2:
            i+=1
            s[i].connect_to(o[j])
            if verbose: print("WARN: Rare edge case during merge.")
        elif other.ch_i(o_left)==other.ch_i(o_right) and len(s)<=2:
            j+=1
            s[i].connect_to(o[j])
            if verbose: print("WARN: Rare edge case during merge.")

        while 1:
            if i+1<len(s) and not self.intersects(s[i+1], o[j]) and not other.intersects(s[i+1], o[j]):
                i+=1
                s[i].connect_to(o[j])
            if j+1<len(o) and not self.intersects(s[i], o[j+1]) and not other.intersects(s[i], o[j+1]):
                j+=1
                s[i].connect_to(o[j])
            if i>=len(s)-1 and j>=len(o)-1:
                break

        self.fix_hull(point_on_hull=self.ch(s_left), thorough=False)
        self.vertex_list[self.current_index+1:len(self.vertex_list)] = sortByDistanceToHull(self.vertex_list[self.current_index+1:len(self.vertex_list)], self)

        #Kill other:
        for v in self.vertex_list:
            if v.claimant==other:
                v.claimant = self
        other.alive = False
        active_iterators.remove(other)

    def __init__(self, startpoint=None):
        global vertices
        # Create starting point and vertex list
        if startpoint is None:
            self.origin = Vertex(explicit_x=randint(0,14000), explicit_y=randint(0,8000))
        else:
            self.origin = startpoint
        self.vertex_list = sortByDistance(vertices, self.origin)

        # First check if we can at least make a triangle at this location. If we can't we may as well toss this iterator
        if(not self.vertex_list[0].occupied and not self.vertex_list[1].occupied and not self.vertex_list[2].occupied and not self.vertex_list[0].on_hull and not self.vertex_list[1].on_hull and not self.vertex_list[2].on_hull):
            self.convex_hull = HDCEL.make_triangle(self.vertex_list[0], self.vertex_list[1], self.vertex_list[2])
            self.vertex_list[0].on_hull = True
            self.vertex_list[1].on_hull = True
            self.vertex_list[2].on_hull = True
            self.vertex_list[0].claimant = self
            self.vertex_list[1].claimant = self
            self.vertex_list[2].claimant = self
            all_iterators.append(self)
            active_iterators.append(self)
            self.current_index = 2
            self.initialized = True
            self.alive = True

    def iterate(self, override=None):
        # Check for status: DEAD
        if not self.alive or self.current_index+1 >= len(self.vertex_list):
            return It_Response.DEAD

        # Pre-iteration prep
        v = None
        if override is not None:
            v = override
        else:
            self.current_index += 1
            v = self.vertex_list[self.current_index]
        i, j = getVisibleBounds(v, self)

        # Check for status: UNABLE_SKIPPED
        if v.on_hull or v.occupied or occluded(v, self.ch(i), self.ch(j), self):
            if verbose and override is not None and occluded(v, self.ch(i), self.ch(j), self): print("OCCLUDED")
            return It_Response.UNABLE_SKIPPED

        # Check for status: ABLE_REFUSED
        # pred = (min(abs(j-i), 4) / 4) * 0.9
        # pred += (min(get_distance(self.origin, v), 10000) / 10000) * 0.1
        # #print(str(pred) + " " + str(self.tolerance))
        # if pred > self.tolerance:
        #     self.current_index -= 1 # Reset index
        #     return It_Response.ABLE_REFUSED

        # Proceed with iteration:
        for u in range(i, j):
            e = getEdge(self.ch(u), self.ch(u+1))
            if(e==None):
                return It_Response.ERROR

            top_is_convex = not isLeftOfEdge(e.twin.prev, v)
            bot_is_convex = not isLeftOfEdge(e.twin.nxt, v)
            e.origin.connect_to(v)

            if top_is_convex and bot_is_convex:
                e.remove()
        self.ch(j).connect_to(v)

        self.update_convex_hull(i, j, v)
        v.on_hull = True
        v.claimant = self

        return It_Response.ABLE_COMPLETED

    def update_convex_hull(self, i, j, v):
        """ Updates the convex hull of an iterator after an iteration.
                input:  index of the left-most visible point from v of the previous convex hull
                        index of the right-most visible point from v of the previous convex hull
                        point that replaces all points in [i, j[ of the convex hull
        """
        i = self.ch_i(i)
        j = self.ch_i(j)
        if j < i:
            for q in self.convex_hull[i+1:len(self.convex_hull)]:
                q.claimant = self
                q.occupied = True
                q.on_hull = False
            self.convex_hull[i+1:len(self.convex_hull)] = [v]
            for q in self.convex_hull[0:j]:
                q.claimant = self
                q.occupied = True
                q.on_hull = False
            self.convex_hull[0:j] = []
        else:
            for q in self.convex_hull[i+1:j]:
                q.claimant = self
                q.occupied = True
                q.on_hull = False
            self.convex_hull[i+1:j] = [v]

def make_new_iterator(attempts=1):
    z = Iterator()
    if(not z.initialized and attempts>1):
        return make_new_iterator(attempts-1)
    return z.initialized

num = 0
def cycle():
    global points
    global num

    goal = 1000
    num += 1
    if num%max(1,int(goal/100))==0: print("\r"+str(int(num*100/goal))+"%", end ='')
    if num > goal: return False

    for it in active_iterators:
        res = it.iterate()
        if res==It_Response.ERROR:
            print("ERROR")
        elif res==It_Response.UNABLE_SKIPPED:
            it.merge(it.vertex_list[it.current_index].claimant)
    return True
