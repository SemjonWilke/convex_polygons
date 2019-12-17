"""@package docstring
Software project for the Computational Geometry Week 2020 competition
"""
import sys
import signal
import argparse
import math
from collections import defaultdict

sys.path.append('./bin')
import HCLUSTER
import HCOMMON
import HDCEL
import HJSON
import HVIS

import algorithm_ben_v1

#  the second approach
# ======================================================================
upper_hull = list()
lower_hull = list()
indices = list()
conv_hulls = list()
vertices = list()

def v2nd_isLeftOf(a, b, v):
    return ((b[0] - a[0])*(v[1] - a[1]) - (b[1] - a[1])*(v[0] - a[0])) >= 0.0

def sort_by_Xcoord():
    global points
    assert(len(points)>2)
    points.sort(key = lambda p: p[0] )

def g_lower_hull():
    global lower_hull, points, indices
    lower_hull.clear()
    if(len(indices) < 3 ):
        lower_hull= indices[:]
        return
    lower_hull.append(indices[-1] )
    lower_hull.append(indices[-2] )
    for i in range(len(indices) - 3, -1, -1):
        while( not v2nd_isLeftOf(points[lower_hull[-1]], points[lower_hull[-2]], points[indices[i]]) ):
            lower_hull.pop()
            if len(lower_hull) < 2:
                break
        lower_hull.append(indices[i])

def g_upper_hull():
    global upper_hull, points, indices
    upper_hull.clear()
    if(len(indices) < 3 ):
        upper_hull= indices[:]
        return
    upper_hull.append(indices[0])
    upper_hull.append(indices[1])
    for i in range(2, len(indices)):
        while(v2nd_isLeftOf(points[upper_hull[-2]], points[upper_hull[-1]], points[indices[i]])):
            upper_hull.pop()
            if len(upper_hull)<2:
                break
        upper_hull.append(indices[i])

def g_upper_most_right(outer_hull, inner_hull):
    _h = -1
    _x = points[conv_hulls[inner_hull][0]][0]
    for i in range(len(conv_hulls[outer_hull]) - 2, -1, -1):
        if _x > points[conv_hulls[outer_hull][i]][0]:
            _h = i+1
            break
    return _h

def g_lower_most_right(outer_hull, inner_hull):
    _l = 0
    _x = points[conv_hulls[inner_hull][0]][0]
    for i in range(1, len(conv_hulls[outer_hull])):
        if _x > points[conv_hulls[outer_hull][i]][0]:
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
                while v2nd_isLeftOf( points[conv_hulls[inner_hull][0]],
                        points[conv_hulls[outer_hull][_l]],
                        points[conv_hulls[outer_hull][_h]]):
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
            if v2nd_isLeftOf(points[conv_hulls[inner_hull][f_in]],
                        points[conv_hulls[inner_hull][l_in]],
                        points[conv_hulls[outer_hull][f_out]]):
                while v2nd_isLeftOf(points[conv_hulls[inner_hull][f_in]],
                        points[conv_hulls[inner_hull][l_in]],
                        points[conv_hulls[outer_hull][l_out]]):
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
            HDCEL.make_hull(vertices, conv_hulls[ch])
            conv_hulls[ch].append(keeper)
        else: HDCEL.make_hull(vertices, conv_hulls[ch])

def depth_search():
    global conv_hulls
    if len(conv_hulls) < 2:
        return
    for i in range(1, len(conv_hulls)):
        if len(conv_hulls[i]) < 3:
            break
        for v in range(len(conv_hulls[i])-1):
            _e = vertices[conv_hulls[i][v]].incidentEdge
            if v2nd_isLeftOf(points[_e.prev.origin.i],
                    points[_e.twin.nxt.twin.origin.i],
                    points[conv_hulls[i][v]]) and v2nd_isLeftOf(points[_e.twin.prev.origin.i],
                    points[_e.nxt.twin.origin.i],
                    points[_e.twin.origin.i]):
                _e.remove()

def g_convex_hull():
    global upper_hull, lower_hull, indices
    assert(len(indices)>0)
    g_lower_hull()
    g_upper_hull()
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

### Main
def exithandler(sig, frame):
    print('Exiting')
    exit(3)

def run(filename, c=(6000, 4500), overwrite=False, plot=False, algorithm=False):
    global convex_hull, points, indices, vertices # make convex_hull algorithm specific

    start_t = HCOMMON.snaptime()
    HDCEL.points = points
    vertices = [HDCEL.Vertex(index=i) for i in range(len(points))]


    '''make sure that only one approach is active when running the program, as they have different terms of sorting'''
    if algorithm: #first approach
        algorithm_ben_v1.run(_vertices=vertices, _origin=HDCEL.Vertex(explicit_x=c[0], explicit_y=c[1]), _verbose=verbose)

    else: #second approach
        if verbose: print("Abbas' Algorithm")
        sort_by_Xcoord()
        indices = [i for i in range(len(points))]
        build_mesh()
    ###------------------------------------------------------------------------

    edges = HDCEL.get_edge_dict(verbose)
    HCOMMON.snapshoot(start_t, "Computation", verbose)

    written = 1
    '''do not turn on this command when the second approach is active, to avoid losing the start point of pest solution, as there is no start point involved in the second approach'''
    # written = HJSON.writeTestSolution(sys.argv[1],instance,c,edges,overwrite) #TODO ugly

    if plot:
        start_t = HCOMMON.snaptime()
        HVIS.drawEdges(edges,points)
        if not algorithm:
            for index,conv in enumerate(conv_hulls):
                for i in range(len(conv)-1):
                    color=["m","r","g"]
                    #HVIS.drawSingleHEdge(conv[i], conv[i+1], color[index % 3])
                    #TODO change SingleHEdge to use HDCEL.Edge lkasd
                    #TODO plot only if edge lkasd exists
        HVIS.drawPoints(points,edges)
        HCOMMON.snapshoot(start_t, "Plotting", verbose)
        HVIS.show()
    return written

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exithandler)
    try:
        parser = argparse.ArgumentParser(description='Bens Algorithm for SoCG')
        parser.add_argument('file')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-c', '--coordinates', type=int, nargs=2, dest='coord', help='Coordinates of starting point')
        group.add_argument('-r', '--random', nargs='?', default=0, dest='rndm', help='Use random starting point with optional seed')
        parser.add_argument('-o', '--overwrite', action='store_true', dest='overwrite', help='Overwrite existing solution if better')
        parser.add_argument('-p', '--plot', action='store_true', dest='plot', help='Show plot')
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Print human readable information')
        parser.add_argument('-a', '--algorithm', action='store_true', dest='algorithm', help='choose algorithm to execute')
        parser.add_argument('-k', '--kmeans', action='store_true', dest='kmeans', help='find clusters with kmeans')
        arguments = parser.parse_args()

        verbose = arguments.verbose
        points,instance = HJSON.readTestInstance(arguments.file)

        HVIS.initVis()
        if arguments.kmeans:
            HCLUSTER.findClusterCenters(points, plot=arguments.plot, verbose=verbose)

        if arguments.coord != None:
            exitcode = run(arguments.file, arguments.coord, arguments.overwrite, \
                            arguments.plot, arguments.algorithm)
        else:
            exitcode = run(arguments.file, HCOMMON.randomstart(points, arguments.rndm, verbose), \
                            arguments.overwrite, arguments.plot, arguments.algorithm)
        if exitcode != 0:
            exit(exitcode)
    except KeyboardInterrupt:
        exit(3)
