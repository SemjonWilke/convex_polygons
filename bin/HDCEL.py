import math

# Sample data for testing
points = []

def isLeftOf(a, b, v, strict=False):
    if strict: return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) > 0
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) >= 0

def isRightOf(a, b, v, strict=False):
    if strict: return not isLeftOf(a, b, v, strict=False)
    return not isLeftOf(a, b, v, strict=True)

# Returns angle between an edge and a hypothetical origin-to-c edge
def angle(edge, c):
    a=edge.nxt.origin
    b=edge.origin

    ang = math.degrees(math.atan2(c.y()-b.y(), c.x()-b.x()) - math.atan2(a.y()-b.y(), a.x()-b.x()))
    return ang + 360 if ang < 0 else ang

# Sets two edges as twins
def twin(e1, e2):
    e1.twin = e2
    e2.twin = e1

# Sets two edges as successors
def chain(e1, e2):
    e1.nxt = e2
    e2.prev = e1

def area(e):
    assert(e.nxt is not None)
    tmp = e
    ret = []
    while tmp.nxt!=e:
        ret.append(tmp.origin)
        tmp = tmp.nxt
    return ret

# Vertex class
class Vertex:
    i = -1
    incidentEdge = None
    explicit_x = None
    explicit_y = None
    occupied = False
    on_hull = False
    claimant = None
    mark = None

    def magnitude(self):
        assert(math.sqrt(self.x()**2 + self.y()**2)>0.0001)
        return math.sqrt(self.x()**2 + self.y()**2)

    def normalized(self):
        l = self.magnitude()
        n = Vertex(self.x()/l, self.y()/l)
        assert(n.magnitude()>0.95 and n.magnitude()<1.05)
        return n

    def mul(self, d):
        return Vertex(self.x()*d, self.y()*d)

    def add(self, x, y):
        return Vertex(self.x()+x, self.y()+y)

    def add(self, v):
        return Vertex(self.x()+v.x(), self.y()+v.y())

    def __eq__(self, v):
        return self.i== v.i

    def __hash__(self):
        return hash(repr(self))

    def x(self):
        if(self.i>-1): return points[self.i][0]
        return self.explicit_x

    def y(self):
        if(self.i>-1): return points[self.i][1]
        return self.explicit_y

    def __init__(self, explicit_x=None, explicit_y=None, index=-1):
        self.i=index
        self.explicit_x=explicit_x
        self.explicit_y=explicit_y

    def __str__(self):
        return "Index: {0} X: {1} Y: {2}".format(self.i,self.x(),self.y())

    def get_convex_incidentEdge(self):
        e = self.incidentEdge
        if e is None: return None
        while angle(e, e.twin.nxt.nxt.origin) < 180:
            e = e.twin.nxt
            if e == self.incidentEdge: return None
        return e.twin

    def get_connected_edges(self):
        ret = []
        if self.incidentEdge==None:
            return ret
        e = self.incidentEdge
        while(True):
            ret.append(e)
            e = e.twin.nxt
            if(e==self.incidentEdge): break
        return ret

    def clear(self):
        self.occupied = False
        self.on_hull = False
        self.claimant = None
        for e in self.get_connected_edges():
            e.remove()
        self.incidentEdge = None

    def get_left_right_edge(self, v):
        min_angle = 99999
        max_angle = -99999

        e = self.incidentEdge

        min_angle_edge = e
        max_angle_edge = e

        while(True):
            angl = angle(e,v)

            if(angl<min_angle):
                min_angle = angl
                min_angle_edge = e
            if(angl>max_angle):
                max_angle = angle(e, v)
                max_angle_edge = e

            e = e.twin.nxt
            if(e==self.incidentEdge): break

        return max_angle_edge, min_angle_edge

    def connect_to(self, v):
        assert(v!=self)

        for e in self.get_connected_edges():
            if e.nxt.origin == v: return e

        if(v.incidentEdge is not None and self.incidentEdge is None):
            return v.connect_to(self).twin

        if(self.incidentEdge is None and v.incidentEdge is None):
            self.incidentEdge = Edge(self)
            v.incidentEdge = Edge(v)

            chain(self.incidentEdge, v.incidentEdge)
            chain(v.incidentEdge, self.incidentEdge)
            twin(self.incidentEdge, v.incidentEdge)
            assert(self.incidentEdge.nxt.origin==v)
            return self.incidentEdge

        if(v.incidentEdge is None):
            left, right = self.get_left_right_edge(v)

            back = Edge(self, None, None)
            forth = Edge(v, None, None)

            chain(right.twin, back)
            chain(back, forth)
            chain(forth, left)

            twin(back, forth)

            v.incidentEdge = forth
            return back

        else:
            s_left, s_right = self.get_left_right_edge(v)
            v_left, v_right = v.get_left_right_edge(self)

            s_to_v = Edge (self, None, None)
            v_to_s = Edge (v, None, None)

            chain(s_right.twin, s_to_v)
            chain(s_to_v, v_left)

            chain(v_right.twin, v_to_s)
            chain(v_to_s, s_left)

            twin(s_to_v, v_to_s)
            return s_to_v

class _list:
    _head = None
    _tail = None
    _size = 0

    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def remove(self, _e):
        if self._size == 0:
            return
        elif self._size == 1:
            self._head = None
            self._tail = None
            self._size = 0
        else:
            if _e.pred == None:
                self._head = _e.succ
                _e.succ.pred = None
            elif _e.succ == None:
                self._tail = _e.pred
                _e.pred.succ = None
            else:
                _e.pred.succ = _e.succ
                _e.succ.pred = _e.pred
            self._size -=1


    def append(self, _e):
        if self._size == 0:
            _e.pred = None
            _e.succ = None
            self._head = _e
            self._tail = _e
        else:
            self._tail.succ = _e
            _e.pred = self._tail
            _e.succ = None
            self._tail = _e

        self._size+=1

    def size(self):
        return self._size

edge_list = _list()

def get_edge_dict(verbose):
    global edge_list
    _set = set()
    if edge_list._size != 0:
        _e = edge_list._head
        while(True):
            if _e.twin not in _set:
                _set.add(_e)
            _e = _e.succ

            if(_e == None):
                break

        e_list = list(_set)
        if verbose: print("number of edges: %i" % (len(e_list)))
        return {'in' : [e.origin.i for e in e_list], 'out' : [e.nxt.origin.i for e in e_list]}
    return dict()

def get_edge_list():
    global edge_list
    _set = set()
    if edge_list._size != 0:
        _e = edge_list._head
        while(True):
            if _e.twin not in _set:
                _set.add(_e)
            _e = _e.succ

            if(_e == None):
                break

        e_list = list(_set)
        return e_list
    return []

def get_full_edge_list():
    global edge_list
    _set = set()
    if edge_list._size != 0:
        _e = edge_list._head
        while(True):
            _set.add(_e)
            _e = _e.succ

            if(_e == None):
                break

        e_list = list(_set)
        return e_list
    return []


# Edge class
class Edge:
    origin = None
    prev = None
    nxt = None
    twin = None
    pred = None  # predecessor in the list
    succ = None   #  successor in the list

    def __init__(self, origin=None, prev=None, nxt=None):
        self.origin=origin;
        self.prev=prev;
        self.nxt=nxt;
        self.twin=twin;
        self.pred = None
        self.succ = None
        edge_list.append(self)

    def __eq__(self, e):
        return repr(self) == repr(e)

    def __hash__(self):
        return hash(repr(self))

    def __str__(self):
        '''could be helpful for testing purposes'''
        return "Origin: {0} Prev: {1} Next: {2} Twin: {3}".format(self.origin, \
                self.prev.origin,self.nxt.origin,self.twin.origin)

    def to_vector(self):
        return Vertex(self.nxt.origin.x() - self.origin.x(), self.nxt.origin.y() - self.origin.y())

    def remove(self, recursive=True):
        edge_list.remove(self)

        if self.nxt!=self.twin:
            self.nxt.prev = self.twin.prev
        if self.prev!=self.twin:
            self.prev.nxt = self.twin.nxt

        # Update incidentEdge if we removed it
        if self.twin.nxt==self:
            self.origin.incidentEdge = None
        elif self.origin.incidentEdge==self:
            self.origin.incidentEdge = self.twin.nxt

        if(recursive): self.twin.remove(False)

# Function to print information on a vertex. Useful for debugging
def print_vertex(v):
    print("Vertex: " + str(v.x()) + " : " + str(v.y()))
    e = v.incidentEdge
    while(True):
            print(e)
            e = e.twin.nxt
            if(e==v.incidentEdge): break

def make_triangle(a, b, c):
    if isRightOf(a, b, c):
        a, b, c = a, c, b

    a.incidentEdge = Edge(a, None, None)
    b.incidentEdge = Edge(b, None, None)
    c.incidentEdge = Edge(c, None, None)

    chain(a.incidentEdge, b.incidentEdge)
    chain(b.incidentEdge, c.incidentEdge)
    chain(c.incidentEdge, a.incidentEdge)

    a.incidentEdge.twin = Edge(b, None, None)
    b.incidentEdge.twin = Edge(c, None, None)
    c.incidentEdge.twin = Edge(a, None, None)

    chain(a.incidentEdge.twin, c.incidentEdge.twin)
    chain(c.incidentEdge.twin, b.incidentEdge.twin)
    chain(b.incidentEdge.twin, a.incidentEdge.twin)

    twin(a.incidentEdge, a.incidentEdge.twin)
    twin(b.incidentEdge, b.incidentEdge.twin)
    twin(c.incidentEdge, c.incidentEdge.twin)

    return [a,b,c]

def get_triangle(a, b, c):
    if isRightOf(a, b, c):
        a, b, c = a, c, b
    return [a, b, c]

def sortByX(vlist):
    rlist = vlist.copy()
    rlist.sort(key=lambda x: x.y()) # first sort by y
    rlist.sort(key=lambda x: x.x())
    return rlist

def cross(o, a, b):
        return (a.x() - o.x()) * (b.y() - o.y()) - (a.y() - o.y()) * (b.x() - o.x())

def get_convex_hull(verts):
    verts = sortByX(verts)

    lower_hull = []
    for v in verts:
        while len(lower_hull) >= 2 and cross(lower_hull[-2], lower_hull[-1], v) < 0: lower_hull.pop()
        lower_hull.append(v)

    upper_hull = []
    for v in reversed(verts):
        while len(upper_hull) >= 2 and cross(upper_hull[-2], upper_hull[-1], v) < 0: upper_hull.pop()
        upper_hull.append(v)

    return lower_hull[:-1] + upper_hull[:-1]

def form_convex_hull(verts):
    h = get_convex_hull(verts)
    for i in range(len(h)):
        h[i-1].connect_to(h[i])

def make_hull(vertices, inds):
    if len(inds) == 1:
            return
    if len(inds) == 2:
        vertices[inds[0]].incidentEdge = Edge(vertices[inds[0]], None, None)
        vertices[inds[1]].incidentEdge = Edge(vertices[inds[1]], None, None)
        twin(vertices[inds[0]].incidentEdge, vertices[inds[1]].incidentEdge)
        chain(vertices[inds[0]].incidentEdge, vertices[inds[1]].incidentEdge)
        chain(vertices[inds[1]].incidentEdge, vertices[inds[0]].incidentEdge)
        return
    j = None
    k = None
    for i in range(len(inds)):
        vertices[inds[i]].incidentEdge = Edge(vertices[inds[i]], None, None)
        if i == len(inds)-1:
            j = 0
        else:
            j = i +1
        vertices[inds[i]].incidentEdge.twin = Edge(vertices[inds[j]], None, None)
        twin(vertices[inds[i]].incidentEdge, vertices[inds[i]].incidentEdge.twin)
    for i in range(len(inds)):
        if i == len(inds)-1:
            j = 0
        else:
            j = i +1
        if i == 0:
            k = len(inds)-1
        else:
            k = i -1
        chain(vertices[inds[i]].incidentEdge, vertices[inds[j]].incidentEdge)
        chain(vertices[inds[i]].incidentEdge.twin, vertices[inds[k]].incidentEdge.twin)

def mark_depth_first(vertex, mark):
    queue = [vertex]

    while len(queue)>0:
        v = queue.pop(0)
        v.mark = mark

        for e in v.get_connected_edges():
            if v.nxt.origin.mark is not None:
                queue.append(e.nxt.origin)
