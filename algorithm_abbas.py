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

def v2nd_isLeftOf(a, b, v):
    return ((b[0] - a[0])*(v[1] - a[1]) - (b[1] - a[1])*(v[0] - a[0])) >= 0.0

def sort_by_Xcoord():
    assert(len(DCEL.points)>2)
    DCEL.points.sort(key = lambda p: p[0] )

def g_lower_half():
    global lower_hull, indices
    lower_hull.clear()
    if(len(indices) < 3 ):
        lower_hull= indices[:]
        return
    lower_hull.append(indices[-1] )
    lower_hull.append(indices[-2] )
    for i in range(len(indices) - 3, -1, -1):
        while( not v2nd_isLeftOf(DCEL.points[lower_hull[-1]], DCEL.points[lower_hull[-2]], DCEL.points[indices[i]]) ):
            lower_hull.pop()
            if len(lower_hull) < 2:
                break
        lower_hull.append(indices[i])

def g_upper_half():
    global upper_hull, indices
    upper_hull.clear()
    if(len(indices) < 3 ):
        upper_hull= indices[:]
        return
    upper_hull.append(indices[0])
    upper_hull.append(indices[1])
    for i in range(2, len(indices)):
        while(v2nd_isLeftOf(DCEL.points[upper_hull[-2]], DCEL.points[upper_hull[-1]], DCEL.points[indices[i]])):
            upper_hull.pop()
            if len(upper_hull)<2:
                break
        upper_hull.append(indices[i])

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

def update_inner_inds(f_in, l_in, inner_hull):
    global conv_hulls
    if len(conv_hulls[inner_hull]) == 2:
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
                vertices[conv_hulls[outer_hull][_h]].connect_to(vertices[conv_hulls[inner_hull][0]])
            else:
                while v2nd_isLeftOf( DCEL.points[conv_hulls[inner_hull][0]],
                        DCEL.points[conv_hulls[outer_hull][_l]],
                        DCEL.points[conv_hulls[outer_hull][_h]]):
                    _h-=1
                vertices[conv_hulls[outer_hull][_h+1]].connect_to(vertices[conv_hulls[inner_hull][0]])
                vertices[conv_hulls[outer_hull][_h]].connect_to(vertices[conv_hulls[inner_hull][0]])
    
    else:
        _l = g_lower_most_right(outer_hull, inner_hull)
        f_in = 0
        l_in = 1
        f_out = _l
        l_out = _l + 1
        tracker = defaultdict(dict)
        att_in = None
        att_out = conv_hulls[outer_hull].pop()
        if len(conv_hulls[inner_hull]) != 2:
            att_in = conv_hulls[inner_hull].pop()

        while True:
            if v2nd_isLeftOf(DCEL.points[conv_hulls[inner_hull][f_in]],
                        DCEL.points[conv_hulls[inner_hull][l_in]],
                        DCEL.points[conv_hulls[outer_hull][f_out]]):
                while v2nd_isLeftOf(DCEL.points[conv_hulls[inner_hull][f_in]],
                        DCEL.points[conv_hulls[inner_hull][l_in]],
                        DCEL.points[conv_hulls[outer_hull][l_out]]):
                    f_out, l_out = update_outer_inds(f_out, l_out, outer_hull)
                if check_tracker(l_in, f_out, inner_hull, outer_hull, tracker):
                    break
                f_in, l_in = update_inner_inds(f_in, l_in, inner_hull)
            else:
                if check_tracker(f_in, l_out, inner_hull, outer_hull, tracker):
                    break
                f_out, l_out = update_outer_inds(f_out, l_out, outer_hull)
        if len(conv_hulls[inner_hull]) != 2:
            conv_hulls[inner_hull].append(att_in)
        conv_hulls[outer_hull].append(att_out)


def construct_hulls():
    global conv_hulls, vertices
    for ch in range(len(conv_hulls)):
        if len(conv_hulls[ch]) > 2:
            keeper = conv_hulls[ch].pop()
            DCEL.make_hull(vertices, conv_hulls[ch])
            conv_hulls[ch].append(keeper)
        else: DCEL.make_hull(vertices, conv_hulls[ch])


def depth_search():
    global conv_hulls
    if len(conv_hulls) < 2:
        return
    for i in range(1, len(conv_hulls)):
        if len(conv_hulls[i]) < 3:
            break
        for v in range(len(conv_hulls[i])-1):
            _e = vertices[conv_hulls[i][v]].incidentEdge
            if v2nd_isLeftOf(DCEL.points[_e.prev.origin.i],
                    DCEL.points[_e.twin.nxt.twin.origin.i],
                    DCEL.points[conv_hulls[i][v]]) and v2nd_isLeftOf(DCEL.points[_e.twin.prev.origin.i],
                    DCEL.points[_e.nxt.twin.origin.i],
                    DCEL.points[_e.twin.origin.i]):
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
    i = 0;
    while len(indices) > 0:
        i += 1
        if verbose:
            print("\r%d / %d" % (i, len(indices)), end="")
            sys.stdout.flush()
        _hull = g_convex_hull()
        conv_hulls.append(_hull)
        #------------------------------------------------------------ bottleneck of computation time
        indices = list( set(indices) - set(_hull) )
        indices.sort()
        #------------------------------------------------------------------- can be replaced by this, but it's even worse!!
        # indices = [ind for ind in indices if ind not in _hull]
        #-----------------------------------------------------------------
    construct_hulls()
    # print("num of hulls: ", len(conv_hulls))
    for i in range(len(conv_hulls)-1):
        connect_2_hulls(i+1, i)
    depth_search()


def run(vbs, verts):
    global verbose
    verbose = vbs
    if verbose: print("Abbas' Algorithm")
    global indices, vertices
    vertices = verts;
    sort_by_Xcoord()
    indices = [i for i in range(len(DCEL.points))]
    build_mesh()

    return DCEL.get_edge_dict(verbose)
