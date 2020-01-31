import sys
sys.path.append('./bin')
import HDCEL as DCEL
from collections import defaultdict


verbose = False

upper_hull = list() 
lower_hull = list()  
indices = list()
conv_hulls = list()
vertices = list()

def _prod(a, b, v):
    return ((b[0] - a[0])*(v[1] - a[1]) - (b[1] - a[1])*(v[0] - a[0]))

def _isLeftOf(a, b, v):
    return _prod(a, b, v) >= 0.0

def _isStrictlyLeftOf(a, b, v):
    return _prod(a, b, v) > 0.0

def _isCollinear(a, b, v):
    return _prod(a, b, v) == 0.0

def sort_by_Xcoord():
    global indices
    assert(len(DCEL.points)>3)
    # DCEL.points.sort(key = lambda p: [p[0], p[1]] )
    indices = [i[0] for i in sorted(enumerate(DCEL.points), key = lambda p: [p[1][0], p[1][1]])]

def g_lower_half():
    global lower_hull, indices
    lower_hull.clear()
    if(len(indices) < 3 ):
        lower_hull= indices[:]
        return
    lower_hull.append(indices[-1] ) 
    lower_hull.append(indices[-2] )
    for i in range(len(indices) - 3, -1, -1):
        while( not _isLeftOf(DCEL.points[lower_hull[-1]], 
                DCEL.points[lower_hull[-2]], DCEL.points[indices[i]]) ):
            lower_hull.pop()
            if len(lower_hull) < 2:
                break
        lower_hull.append(indices[i])
    indices = [ind for ind in indices if ind not in lower_hull[1:-1]]

def g_upper_half():
    global upper_hull, indices
    upper_hull.clear()
    if(len(indices) < 3 ):
        upper_hull= indices[:]
        indices = list( set(indices) - set(upper_hull) )
        indices.sort()
        return
    upper_hull.append(indices[0])
    upper_hull.append(indices[1])
    for i in range(2, len(indices)):
        while(_isStrictlyLeftOf(DCEL.points[upper_hull[-2]],  
                DCEL.points[upper_hull[-1]], DCEL.points[indices[i]])):
            upper_hull.pop()
            if len(upper_hull)<2:
                break
        upper_hull.append(indices[i])
    indices = [ind for ind in indices if ind not in upper_hull]

def g_upper_most_right(outer_hull, inner_hull):
    _h = -1
    _x = DCEL.points[conv_hulls[inner_hull][0]][0]
    for i in range(len(conv_hulls[outer_hull]) - 2, -1, -1):
        if _x > DCEL.points[conv_hulls[outer_hull][i]][0]:
            _h = i+1
            break
    return _h

def g_lower_most_right(outer_hull, inner_hull):
    _l = 0
    _x = DCEL.points[conv_hulls[inner_hull][0]][0]
    for i in range(1, len(conv_hulls[outer_hull])):
        if _x > DCEL.points[conv_hulls[outer_hull][i]][0]:
            _l = i-1
            break
    return _l


def update_inner_inds(f_in, l_in, inner_hull, _Coll):
    global conv_hulls
    if len(conv_hulls[inner_hull]) == 2 or _Coll:
        f_in, l_in = l_in, f_in
    else:
        f_in = l_in
        if l_in == len(conv_hulls[inner_hull])-1:
            l_in = 0
        else: 
            l_in +=1
    return f_in, l_in

def update_outer_inds(f_out, l_out, outer_hull):
    global conv_hulls
    f_out = l_out
    if l_out == len(conv_hulls[outer_hull])-1:
        l_out = 0
    else:
        l_out+=1
    return f_out, l_out

def shift_ind(f_in, l_in, inner_hull):
    global conv_hulls
    if len(conv_hulls[inner_hull]) <= 2:
        return
    curr = l_in+1
    if l_in == len(conv_hulls[inner_hull])-1:
        curr=0
    while _isCollinear(DCEL.points[conv_hulls[inner_hull][f_in]], 
            DCEL.points[conv_hulls[inner_hull][l_in]],
            DCEL.points[conv_hulls[inner_hull][curr]]):
        l_in = curr
        if curr == len(conv_hulls[inner_hull])-1:
            curr = 0
        else:
            curr+=1
    return l_in


def check_tracker(_from, _to, inner_hull, outer_hull, tracker):
    global conv_hulls
    if (_from not in tracker) or (_to not in tracker[_from]):
            tracker[_from][_to] = 1
            vertices[conv_hulls[outer_hull][_to]].connect_to(vertices[conv_hulls[inner_hull][_from]])
            return False
    return True

def connect_2_hulls(inner_hull, outer_hull):
    global conv_hulls, vertices
    assert(len(conv_hulls)>0 and inner_hull < len(conv_hulls) and outer_hull < len(conv_hulls) and inner_hull==outer_hull+1)  # just for debugging, can be removed
    if len(conv_hulls[inner_hull]) == 1:
        if len(conv_hulls[outer_hull]) == 4:
            for i in range(3):
                vertices[conv_hulls[outer_hull][i]].connect_to(vertices[conv_hulls[inner_hull][0]])
        else:
            _l = g_lower_most_right(outer_hull, inner_hull)
            _h = g_upper_most_right(outer_hull, inner_hull)
            vertices[conv_hulls[outer_hull][_l]].connect_to(vertices[conv_hulls[inner_hull][0]])
            if _l == 0 and _h == len(conv_hulls[outer_hull])-1:
                vertices[conv_hulls[outer_hull][_l+1]].connect_to(vertices[conv_hulls[inner_hull][0]])
                vertices[conv_hulls[outer_hull][_h-1]].connect_to(vertices[conv_hulls[inner_hull][0]])
            else:
                while _isLeftOf( DCEL.points[conv_hulls[inner_hull][0]],
                        DCEL.points[conv_hulls[outer_hull][_l]],
                        DCEL.points[conv_hulls[outer_hull][_h]]):
                    _h-=1
                vertices[conv_hulls[outer_hull][_h+1]].connect_to(vertices[conv_hulls[inner_hull][0]])
                if not _isCollinear(DCEL.points[conv_hulls[inner_hull][0]],
                        DCEL.points[conv_hulls[outer_hull][_l]],
                        DCEL.points[conv_hulls[outer_hull][_h]]):
                    vertices[conv_hulls[outer_hull][_h]].connect_to(vertices[conv_hulls[inner_hull][0]])           
    else:
        _l = g_lower_most_right(outer_hull, inner_hull)
        Coll = False
        f_in = 0
        l_in = 1
        f_out = _l
        l_out = _l + 1
        tracker = defaultdict(dict)
        att_in = None
        att_out = conv_hulls[outer_hull].pop()
        if len(conv_hulls[inner_hull]) != 2:
            att_in = conv_hulls[inner_hull].pop()
        if conv_hulls[inner_hull][0] != conv_hulls[inner_hull][-1] and _isCollinear(DCEL.points[conv_hulls[inner_hull][0]], 
                DCEL.points[conv_hulls[inner_hull][1]], 
                DCEL.points[conv_hulls[inner_hull][-1]]) and _isCollinear(DCEL.points[conv_hulls[inner_hull][-1]], 
                DCEL.points[conv_hulls[inner_hull][-2]], DCEL.points[conv_hulls[inner_hull][0]]):
                Coll = True
                l_in = len(conv_hulls[-1])-1
        while True:
            if not Coll:
                l_in = shift_ind(f_in, l_in, inner_hull) 
            if _isLeftOf(DCEL.points[conv_hulls[inner_hull][f_in]],
                        DCEL.points[conv_hulls[inner_hull][l_in]], 
                        DCEL.points[conv_hulls[outer_hull][f_out]]):
                while _isLeftOf(DCEL.points[conv_hulls[inner_hull][f_in]],
                        DCEL.points[conv_hulls[inner_hull][l_in]], 
                        DCEL.points[conv_hulls[outer_hull][l_out]]):
                    f_out, l_out = update_outer_inds(f_out, l_out, outer_hull) 
                if check_tracker(l_in, f_out, inner_hull, outer_hull, tracker):
                    break
                f_in, l_in = update_inner_inds(f_in, l_in, inner_hull, Coll)
            else:
                if check_tracker(f_in, l_out, inner_hull, outer_hull, tracker):
                    break
                f_out, l_out = update_outer_inds(f_out, l_out, outer_hull)
        if len(conv_hulls[inner_hull]) != 2:
            conv_hulls[inner_hull].append(att_in)
        conv_hulls[outer_hull].append(att_out)

def construct_hulls():
    global conv_hulls, vertices
    for ch in range(len(conv_hulls)-1):
        if len(conv_hulls[ch]) > 2:
            keeper = conv_hulls[ch].pop()
            DCEL.make_hull(vertices, conv_hulls[ch])
            conv_hulls[ch].append(keeper)
        else: DCEL.make_hull(vertices, conv_hulls[ch])
    if len(conv_hulls[-1]) < 3:
        DCEL.make_hull(vertices, conv_hulls[-1])
    else:
        ch = conv_hulls[-1];
        keeper = ch.pop()
        if _isCollinear(DCEL.points[ch[0]], DCEL.points[ch[1]], 
                DCEL.points[ch[-1]]) and _isCollinear(DCEL.points[ch[-1]],
                DCEL.points[ch[-2]], DCEL.points[ch[0]]):

            DCEL.make_hull(vertices, ch[0:2])
            for i in range(1,len(ch)-1):
                vertices[ch[i]].connect_to(vertices[ch[i+1]]) 
        else:    
            DCEL.make_hull(vertices, ch)
        ch.append(keeper)

def __deg(_e):
    if _e == None:
        return 0
    _deg = 1
    __e = _e
    while __e.twin.nxt != _e:
        _deg+=1
        __e = __e.twin.nxt
    return _deg


def depth_search():
    global conv_hulls
    if len(conv_hulls) < 2:
        return
    for i in range(1, len(conv_hulls)-1):
    # for i in range(1, len(conv_hulls)):
        if len(conv_hulls[i]) < 3:
            break
        for v in range(len(conv_hulls[i])-1):
            _e = vertices[conv_hulls[i][v]].incidentEdge
            if _isLeftOf(DCEL.points[_e.prev.origin.i],
                    DCEL.points[_e.twin.nxt.twin.origin.i],
                    DCEL.points[conv_hulls[i][v]]) and _isLeftOf(DCEL.points[_e.twin.prev.origin.i], 
                    DCEL.points[_e.nxt.twin.origin.i], 
                    DCEL.points[_e.twin.origin.i]):
                    if(__deg(_e)>2 and __deg(vertices[conv_hulls[i][v+1]].incidentEdge)>2):
                        _e.remove()

def g_convex_hull():
    global upper_hull, lower_hull, indices
    assert(len(indices)>0)
    g_lower_half()
    g_upper_half()
    if (len(lower_hull) == 2 and len(upper_hull) ==2) or (len(lower_hull) == 1 and len(upper_hull) == 1):
        return lower_hull.copy()
    else:
        lower_hull.extend(upper_hull[1:len(upper_hull)])

    return lower_hull.copy()


def build_mesh():
    global upper_hull, lower_hull, indices, conv_hulls, vertices
    while len(indices) > 0:
        _hull = g_convex_hull()
        conv_hulls.append(_hull)
    construct_hulls()
    for i in range(len(conv_hulls)-1):
        connect_2_hulls(i+1, i)
    depth_search()



def run(vbs, verts):
    global verbose, vertices
    verbose = vbs
    if verbose: print("Abbas' Algorithm")
    vertices = verts

    sort_by_Xcoord()
    
    build_mesh()

    # return DCEL.get_edge_dict(verbose)

    
