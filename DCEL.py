import math

# Sample data for testing
points = dict()
#points['x'] = [0, 1, 0, 1]
#points['y'] = [0, 0, 1, 1]

# Returns angle between an edge and a origin-c edge
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

# Vertex class
class Vertex:
    i = -1
    incidentEdge = None
    explicit_x = None
    explicit_y = None

    def __eq__(self, v):
        return self.i== v.i

    def __hash__(self):
        return hash(repr(self))

    def x(self):
        if(self.i>-1): return points['x'][self.i]
        return self.explicit_x

    def y(self):
        if(self.i>-1): return points['y'][self.i]
        return self.explicit_y

    def __init__(self, explicit_x=None, explicit_y=None, index=-1):
        self.i=index
        self.explicit_x=explicit_x
        self.explicit_y=explicit_y

    def __str__(self):
        return "Index: {0} X: {1} Y: {2}".format(self.i,self.x(),self.y())

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
        assert(self.incidentEdge!=None)

        if(v.incidentEdge==None):
            left, right = self.get_left_right_edge(v)

            back = Edge(self, None, None)
            forth = Edge(v, None, None)

            chain(right.twin, back)
            chain(back, forth)
            chain(forth, left)

            twin(back, forth)

            v.incidentEdge = forth

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

edge_list = []

def get_edge_dict():
    global edge_list
    _set = set()
    for e in edge_list:
        if e.twin not in _set:
            _set.add(e)
    edge_list = list(_set)
    ret = {'in' : [e.origin.i for e in edge_list], 'out' : [e.nxt.origin.i for e in edge_list]}
    return ret


# Edge class
class Edge:
    origin = None
    prev = None
    nxt = None
    twin = None

    def __init__(self, origin=None, prev=None, nxt=None):
        self.origin=origin;
        self.prev=prev;
        self.nxt=nxt;
        self.twin=twin;
        edge_list.append(self)

    def __eq__(self, e):
        return repr(self) == repr(e)

    def __hash__(self):
        return hash(repr(self))

    def __str__(self):
        '''could be helpful for testing purposes'''
        return "Origin: {0} Prev: {1} Next: {2} Twin: {3}".format(self.origin, \
                self.prev.origin,self.nxt.origin,self.twin.origin)

    def remove(self, recursive=True):
        edge_list.remove(self)
        self.nxt.prev = self.twin.prev
        self.prev.nxt = self.twin.nxt

        if(self.origin.incidentEdge==self):
            assert(self.twin.nxt!=self)
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

"""
#Testing

t1 = Vertex(0)
t2 = Vertex(1)
t3 = Vertex(2)

t1.incidentEdge = Edge(t1, None, None)
t2.incidentEdge = Edge(t2, None, None)
t3.incidentEdge = Edge(t3, None, None)

chain(t1.incidentEdge, t2.incidentEdge)
chain(t2.incidentEdge, t3.incidentEdge)
chain(t3.incidentEdge, t1.incidentEdge)

t1.incidentEdge.twin = Edge(t2, None, None)
t2.incidentEdge.twin = Edge(t3, None, None)
t3.incidentEdge.twin = Edge(t1, None, None)

chain(t1.incidentEdge.twin, t3.incidentEdge.twin)
chain(t3.incidentEdge.twin, t2.incidentEdge.twin)
chain(t2.incidentEdge.twin, t1.incidentEdge.twin)

twin(t1.incidentEdge, t1.incidentEdge.twin)
twin(t2.incidentEdge, t2.incidentEdge.twin)
twin(t3.incidentEdge, t3.incidentEdge.twin)


###############################

t4 = Vertex(3)
t2.connect_to(t4)
t3.connect_to(t4)
t2.incidentEdge.twin.nxt.twin.nxt.remove()

print_vertex(t1)
print_vertex(t2)
print_vertex(t3)
print_vertex(t4)
"""
