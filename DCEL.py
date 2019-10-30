import numpy as np
from uuid import uuid4
from collections import defaultdict

class vertex:
    def __init__(self, x=None, y=None):
        self.x=x;       # floating
        self.y=y;       # floating

class edg_ind:
    def __init__(self, first=None, second=None):
        self.first=first;   # u-int 'origin vertex'
        self.second=second; # u-int 'destination vertex'

    def __eq__(self, _ind):
        return self.first == _ind.first and self.second == _ind.second

    def __str__(self):
        '''could be helpful for testing purposes'''
        return "({0}, {1})".format(self.first,self.second)

class edge:
    def __init__(self,
            ind=None,         # edg_ind
            orig=None,        # u-int  'vertex'
            incident_f=None,  # string 'face-id'
            prev=None,        # edg_ind
            _next=None        # edg_ind
            ):

        self.ind=ind                 # edg_ind
        self.orig=orig;              # u-int 'vertex'
        self.incident_f = incident_f # string 'face-id'
        self.prev=prev;              # edg_ind
        self.next=_next;             # edg_ind
#         self.twin=twin;            # edg_ind  ,  no needed, just swap between first and last of ind


    def __str__(self):
        '''could be helpful for testing purposes'''
        return "Edge: {0} Orig: {1} InceF: {2} Prev: {3} Next: {4} ".format(self.ind,self.orig,self.incident_f,self.prev,self.next)

class dcel_stuct:

    def __init__(self, data=None):
        self.data=defaultdict(np.array) # a dictionary that maps a vertex to an array of outgoing edges

    def __call__(self, _ind):
        if _ind.first in self.data:
            for i in range(self.data[_ind.first].shape[0]):
                if self.data[_ind.first][i].ind == _ind:
                    return self.data[_ind.first][i]
        return None

    def add_edg(self, _from, edg):
        if _from in self.data:
            self.data[_from] = np.append(self.data[_from], edg)
        else:
            self.data[_from] = np.array([edg])

    def set_prev(self, _ind, prev):
        if _ind.first in self.data:
            for i in range(self.data[_ind.first].shape[0]):
                if self.data[_ind.first][i].ind == _ind:
                    self.data[_ind.first][i].prev = prev

    def set_next(self, _ind, _next):
        if _ind.first in self.data:
            for i in range(self.data[_ind.first].shape[0]):
                if self.data[_ind.first][i].ind == _ind:
                    self.data[_ind.first][i].next = _next

    def set_orig(self, _ind, orig):
        if _ind.first in self.data:
            for i in range(self.data[_ind.first].shape[0]):
                if self.data[_ind.first][i].ind == _ind:
                    self.data[_ind.first][i].orig = orig

    def set_incedent_f(self, _ind, incident_f):
        if _ind.first in self.data:
            for i in range(self.data[_ind.first].shape[0]):
                if self.data[_ind.first][i].ind == _ind:
                    self.data[_ind.first][i].incident_f = incident_f


    def get_edg(self, _ind):

        if _ind.first in self.data:
            for i in range(self.data[_ind.first].shape[0]):
                if self.data[_ind.first][i].ind == _ind:
                    return self.data[_ind.first][i]
        return None

    def remove_edg(self, _ind):
        if _ind.first in self.data:
            for i in range(self.data[_ind.first].shape[0]):
                if self.data[_ind.first][i].ind == _ind:
                    self.data[_ind.first] = np.delete(self.data[_ind.first], i)
                    return
    # def key(self, _ind):
    #     return str(_ind.first)+str(_ind.second)

class DCEL:

    def __init__(self, data=None):
        self.vertices = np.array(data)     # array of vertex
        self.faces = dict()                # maps face-IDs to array of vertices
        self.incidentFaces = defaultdict(set)  # maps vertices to face-IDs
        self.data = dcel_stuct()    # dcel entities

    def sharedFaces(self, vert1, vert2):
        '''return a faces, that two vertices share, None if they don't share any'''
        if len(self.incidentFaces[vert1]) != 0 and len(self.incidentFaces[vert2]) != 0 :
            shared_f = self.incidentFaces[vert1].intersection(self.incidentFaces[vert2])
            if len(shared_f) == 0:
                return None
            return shared_f # next(iter(shared_f))

    def most_leftEdg(self,
                     face_1, # face-id
                     v1,      # u-int 'vertex'
                     v2       # u-int 'vertex'
                    ):
        '''return the most left edge fo a given vertex within a given face'''
        _edg1 = None
        _edg2 = None
        for i in range(self.faces[face_1].shape[0]):
            if i==0 and self.faces[face_1][i] == v1:      # oriented to left
                _edg1 = self.data.get_edg(edg_ind(self.faces[face_1][-1] , v1))
                if _edg1.incident_f != face_1:            # oriented to right
                    _edg1 = self.data.get_edg(edg_ind(v1, self.faces[face_1][-1] ))
            elif self.faces[face_1][i] == v1:             # oriented to left
                _edg1 = self.data.get_edg(edg_ind(self.faces[face_1][i-1] , v1))
                if _edg1.incident_f != face_1:            # to right
                    _edg1 = self.data.get_edg(edg_ind(v1, self.faces[face_1][i-1] ))

            if i==0 and self.faces[face_1][i] == v2:      # oriented to left
                _edg2 = self.data.get_edg(edg_ind(self.faces[face_1][-1] , v2))
                if _edg2.incident_f != face_1:            # oriented to right
                    _edg2 = self.data.get_edg(edg_ind(v2, self.faces[face_1][-1] ))
            elif self.faces[face_1][i] == v2:             # to left
                _edg2 = self.data.get_edg(edg_ind(self.faces[face_1][i-1] , v2))
                if _edg2.incident_f != face_1:            # to right
                    _edg2 = self.data.get_edg(edg_ind(v2, self.faces[face_1][i-1] ))

        return _edg1, _edg2

    def split_face(self,
                   face_id, # face
                   _from,   # u-int 'vertex'
                   _to      # u-int 'vertex'
                  ):
        '''divide a given face by an edge between two vertices'''
        ind1, = np.where(self.faces[face_id] == _from)
        ind2, = np.where(self.faces[face_id] == _to)
        if(abs(ind1[0]-ind2[0])<=1):
            return # already an edge between '_from' and '_to'
        else:
            r_face = None
            l_face = None
            if ind2[0]>ind1[0]:
                x, y, z = np.split(self.faces[face_id], [ind1[0],ind2[0]])
                r_face = np.append(y, z[0])
                l_face = np.append(z,np.append(x,y[0]))
            else:
                x, y, z = np.split(self.faces[face_id], [ind2[0],ind1[0]])
                r_face = np.append(z,np.append(x,y[0]))
                l_face = np.append(y, z[0])

        return r_face, l_face

    def addEdg(self,
               _from,  # u-int 'vertex'
               _to,    # u-int 'vertex'
                ):
        '''add an edge between two vertices'''

        shared_f = self.sharedFaces(_from, _to)
        if shared_f == None:
            # TODO
            print('dummy')

        else:
            _e11, _e12 = self.most_leftEdg(shared_f, _from, _to)
            r_face, l_face = self.split_face( shared_f, _from, _to)
            rf_id = uuid4()
            self.faces[shared_f] = l_face;
            self.faces[rf_id] = r_face
            for i in range(1, r_face.shape[0]-1):
                self.incidentFaces[r_face[i]].discard(shared_f)
                self.incidentFaces[r_face[i]].add(rf_id)
            self.incidentFaces[r_face[0]].add(rf_id)
            self.incidentFaces[r_face[-1]].add(rf_id)

            _e1 = None
            _e2 = None
            if _e11.ind.second == _from:  # right-to-left
                _e1 = edge(edg_ind(_from, _to), _from, shared_f, _e11.ind, _e12.next)
                _e2 = edge(edg_ind(_to, _from), _to, rf_id, _e12.ind, _e12.prev)
                self.data.add_edg(_from, _e1)    # add new edge
                self.data.add_edg(_to, _e2)      # add twin of new edge

                temp = self.data(_e11.ind)
                if temp != None:
                    self.data.set_prev(temp.next, _e2.ind)
                    self.data.set_next(_e11.ind, _e1.ind)

                temp = self.data(_e12.ind)
                if temp != None:
                    self.data.set_prev(temp.next, _e1.ind)
                    self.data.set_next(temp.ind, _e2.ind)
                    self.data.set_incedent_f(temp.ind, rf_id);

                temp = _e2.next
                while temp != _e12.ind:
                    self.data.set_incedent_f(temp, rf_id);
                    temp = self.data(temp).next

            else:       # left-to-right
                _e1 = edge(edg_ind(_to, _from), _to, shared_f, _e12.prev, _e11.ind)
                _e2 = edge(edg_ind(_from, _to), _from, rf_id, _e11.prev, _e12.ind)
                self.data.add_edg(_to, _e1)
                self.data.add_edg(_from, _e2)

                temp = self.data(_e11.ind)
                if temp != None:
                    self.data.set_next(temp.prev, _e2.ind)
                    self.data.set_prev(_e11.ind, _e1.ind)

                temp = self.data(_e12.ind)
                if temp != None:
                    self.data.set_next(temp.prev, _e1.ind)
                    self.data.set_prev(_e12.ind, _e2.ind)
                    self.data.set_incedent_f(temp.ind, rf_id);

                temp = _e2.prev
                while temp != _e12.ind:
                    self.data.set_incedent_f(temp, rf_id);
                    temp = self.data(temp).prev

    def removeEdg(self,
                    _ind #  edg_ind
                    ):
        '''remove an edge and its twin, and combine the faces at sides in one'''

        shared_f = self.sharedFaces(_ind.first, _ind.second)
        if len(shared_f) < 2:
            # TODO
            print('dummy')

        else:
            face_1 = shared_f.pop()
            face_2 = shared_f.pop()
            _merged = self.mergeSet(face_1, face_2, _ind.first, _ind.second)
            _twin = self.flip_edg(_ind)

            if self.data(_ind).incident_f == face_1:
                temp = self.data(self.data(_ind).next)
                while temp.ind != _ind:
                    self.data.set_incedent_f(temp.ind, face_2);
                    self.incidentFaces[temp.orig].discard(face_1)
                    self.incidentFaces[temp.orig].add(face_2)
                    temp = self.data(temp.next)
                self.faces[face_2] = _merged
                del self.faces[face_1]

            else:
                temp = self.data(self.data(_twin).next)
                while temp.ind != _twin:
                    self.data.set_incedent_f(temp.ind, face_1);
                    self.incidentFaces[temp.orig].discard(face_2)
                    self.incidentFaces[temp.orig].add(face_1)
                    temp = self.data(temp.next)
                self.faces[face_1] = _merged
                del self.faces[face_2]

            self.data.set_next(self.data(_ind).prev, self.data(_twin).next)
            self.data.set_prev(self.data(_twin).next, self.data(_ind).prev,)
            self.data.set_next(self.data(_twin).prev, self.data(_ind).next )
            self.data.set_prev(self.data(_ind).next, self.data(_twin).prev)
            self.data.remove_edg(_ind)
            self.data.remove_edg(_twin)

    def flip_edg(self, _ind):
        return edg_ind(_ind.second, _ind.first)

    def addFace(self, verts):
        '''add a face from an array of vertices'''
        face_id = uuid4();
        self.faces[face_id] = verts
        for i in range(verts.shape):
            self.incidentFaces[verts[i]].add(face_id)

    def addVert(self, vert):  # this should not be needed, as the num of vertices do not change!
        self.vertices = np.append(self.vertices, vert)

    def v_isLeftTo(self,
            _from,  # u-int  'vertex'
            _to,    # u-int  'vertex'
            _vert   # u-int  'vertex'
            ):
        '''check if the vertex '_vert' is on the left of line going through vertices '_from' and '_to'  '''
        return ((self.vertices[_to].x - self.vertices[_from].x)
                    *(self.vertices[_vert].y - self.vertices[_from].y)
                    - (self.vertices[_to].y - self.vertices[_from].y)
                    *(self.vertices[_vert].x - self.vertices[_from].x)) <= 0;

    def e_isLeftTo(self,
        edg,   # edg_ind
        vert,  # u-int 'vertex'
        ):
        '''check if the vertex 'vert' is on the left of edge 'edg'  '''
        return self.v_isLeftTo(self.data(edg).orig,
                          self.data(self.data(edg).next).orig,
                          vert);

    def mergeSet(self,
            a,   # face-id
            b,   # face-id
            f,   # u-int "vertex, the origin of edge"
            l    # u-int "vertex, destination of edge"
            ):
        '''merge two faces that consist of two arrays of vertices into one at a place of a given edge'''
        '''this has been done in very naive way! maybe someone else can rewrite it in better way'''
        a = self.faces[a]
        b = self.faces[b]
        if (f not in a) or (f not in b) or (l not in a) or (l not in b):
            return None

        _merged = None
        f1, = np.where(a == f)
        l1, = np.where(a == l)
        f2, = np.where(b == f)
        l2, = np.where(b == l)
        if abs(f1[0]-l1[0]) == 1 and abs(f2[0]-l2[0]) == 1:
            '''next to each other ordered'''
            if f1[0] > l1[0] and f2[0] > l2[0]:
                '''left-left orinted '''
                b = np.flip(b)
                f2, = np.where(b == f)
                l2, = np.where(b == l)
                x1, y1, z1 = np.split(a, [l1[0], f1[0]])
                x2, y2, z2 = np.split(b, [f2[0], l2[0]])
                _merged = np.append(np.append(np.append(x1, z2), x2), z1)

            elif f1[0] < l1[0] and f2[0] < l2[0]:
                '''right-right orinted'''
                a = np.flip(a)
                f1, = np.where(a == f)
                l1, = np.where(a == l)
                x1, y1, z1 = np.split(a, [l1[0], f1[0]])
                x2, y2, z2 = np.split(b, [f2[0], l2[0]])
                _merged = np.append(np.append(np.append(x1, z2), x2), z1)

            elif f1[0] < l1[0] and f2[0] > l2[0]:
                '''right-left orinted'''
                x1, y1, z1 = np.split(a, [f1[0], l1[0]])
                x2, y2, z2 = np.split(b, [l2[0], f2[0]])
                _merged = np.append(np.append(np.append(x1, z2), x2), z1)

            else:
                '''left-right orinted'''
                x1, y1, z1 = np.split(a, [l1[0], f1[0]])
                x2, y2, z2 = np.split(b, [f2[0], l2[0]])
                _merged = np.append(np.append(np.append(x1, z2), x2), z1)


        elif (abs(f1[0]-l1[0]) > 1 and abs(f2[0]-l2[0]) == 1) or (abs(f1[0]-l1[0]) == 1 and abs(f2[0]-l2[0]) > 1):
            '''mixed ordere'''
            if abs(f1[0]-l1[0]) == 1 and abs(f2[0]-l2[0]) > 1:
                _temp = a
                a = b
                b = _temp
                f1, = np.where(a == f)
                l1, = np.where(a == l)
                f2, = np.where(b == f)
                l2, = np.where(b == l)

            if f1[0] > l1[0] and f2[0] > l2[0]:
                '''left-left orinted '''
                x1, y1, z1 = np.split(a, [l1[0], f1[0]])
                x2, y2, z2 = np.split(b, [l2[0], f2[0]])
                _merged = np.append(np.append(y1, z2), x2)

            elif f1[0] < l1[0] and f2[0] < l2[0]:
                '''right-right orinted '''
                x1, y1, z1 = np.split(a, [f1[0], l1[0]])
                x2, y2, z2 = np.split(b, [f2[0], l2[0]])
                _merged = np.append(np.append(y1, z2), x2)

            elif f1[0] < l1[0] and f2[0] > l2[0]:
                '''right-left orinted '''
                b = np.flip(b)
                f2, = np.where(b == f)
                l2, = np.where(b == l)
                x1, y1, z1 = np.split(a, [f1[0], l1[0]])
                x2, y2, z2 = np.split(b, [f2[0], l2[0]])
                _merged = np.append(np.append(y1, z2), x2)

            else:
                '''left-right orinted '''
                b = np.flip(b)
                f2, = np.where(b == f)
                l2, = np.where(b == l)
                x1, y1, z1 = np.split(a, [l1[0], f1[0]])
                x2, y2, z2 = np.split(b, [l2[0], f2[0]])
                _merged = np.append(np.append(y1, z2), x2)

        else:
            '''placed at sides '''
            if f1[0] > l1[0] and f2[0] > l2[0]:
                '''left-left orinted '''
                a = np.flip(a)
                f1, = np.where(a == f)
                l1, = np.where(a == l)
                x1, y1, z1 = np.split(a, [f1[0], l1[0]])
                x2, y2, z2 = np.split(b, [l2[0], f2[0]])
                _merged = np.append(y1, y2)

            elif f1[0] < l1[0] and f2[0] < l2[0]:
                '''right-right orinted '''
                b = np.flip(b)
                f2, = np.where(b == f)
                l2, = np.where(b == l)
                x1, y1, z1 = np.split(a, [f1[0], l1[0]])
                x2, y2, z2 = np.split(b, [l2[0], f2[0]])
                _merged = np.append(y1, y2)

            elif f1[0] < l1[0] and f2[0] > l2[0]:
                '''right-left orinted '''
                x1, y1, z1 = np.split(a, [f1[0], l1[0]])
                x2, y2, z2 = np.split(b, [l2[0], f2[0]])
                _merged = np.append(y1, y2)

            else:
                '''left-right orinted '''
                x1, y1, z1 = np.split(a, [l1[0], f1[0]])
                x2, y2, z2 = np.split(b, [f2[0], l2[0]])
                _merged = np.append(y1, y2)

        return _merged
