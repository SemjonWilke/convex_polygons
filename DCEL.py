import math


# Sample data for testing
points = dict()
points['x'] = [0, 1, 0, 1]
points['y'] = [0, 0, 1, 1]


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
    
    def x(self):
        return points['x'][self.i]
    
    def y(self):
        return points['y'][self.i]
    
    def __init__(self, i):
        self.i=i
        
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

    def __str__(self):
        '''could be helpful for testing purposes'''
        return "Origin: {0} Prev: {1} Next: {2} Twin: {3}".format(self.origin,self.prev.origin,self.nxt.origin,self.twin.origin)
        
    def remove(self, recursive=True):
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
