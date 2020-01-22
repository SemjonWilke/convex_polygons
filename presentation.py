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
import algorithm_ben_v2
import algorithm_ben_v3
import algorithm_abbas

### Main
def exithandler(sig, frame):
    print('Exiting')
    exit(3)

def run(filename, c=(6000, 4500), overwrite=False, plot=False, algorithm="", startpoints=None, explicit=0):
    global convex_hull, points, indices, vertices # make convex_hull algorithm specific

    start_t = HCOMMON.snaptime()
    HDCEL.points = points
    vertices = [HDCEL.Vertex(index=i) for i in range(len(points))]


    '''make sure that only one approach is active when running the program, as they have different terms of sorting'''
    if algorithm == "ben_v1":
        algorithm_ben_v1.run(_vertices=vertices, _origin=HDCEL.Vertex(explicit_x=c[0], explicit_y=c[1]), _verbose=verbose)

    if algorithm == "ben_v2":
        algorithm_ben_v2.run(_vertices=vertices, _startpoints=startpoints, _verbose=verbose)

    if algorithm == "ben_v3":
        algorithm_ben_v3.run(_vertices=vertices, _startpoints=startpoints, _verbose=verbose, _explicit=explicit)

    if algorithm == "abbas":
        algorithm_abbas.run(verbose, vertices)
    ###------------------------------------------------------------------------

    edges = HDCEL.get_edge_dict(verbose)
    HCOMMON.snapshoot(start_t, "Computation", verbose)

    written = HJSON.writeTestSolution(filename,instance,c,edges,overwrite,algorithm)

    if plot:
        start_t = HCOMMON.snaptime()
        HVIS.drawEdges(edges,points)
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
        parser.add_argument('-a', '--algorithm', type=str, dest='algorithm', default="ben_v1", choices=["ben_v1", "ben_v2", "ben_v3", "abbas"], help='choose algorithm to execute')
        parser.add_argument('-s', '--startpoints', type=str, dest='startpoints', help='Starting points for ben_v2 algorithm')
        parser.add_argument('-e', '--explicit', type=int, default=0, dest='explicit', help='Amount of explicit starting points to take from startpoints argument')
        arguments = parser.parse_args()

        verbose = arguments.verbose
        points,instance = HJSON.readTestInstance(arguments.file)

        HVIS.initVis()
        if arguments.coord != None:
            exitcode = run(arguments.file, arguments.coord, arguments.overwrite, \
                            arguments.plot, arguments.algorithm, arguments.startpoints, arguments.explicit)
        else:
            exitcode = run(arguments.file, HCOMMON.randomstart(points, arguments.rndm, verbose), \
                            arguments.overwrite, arguments.plot, arguments.algorithm, arguments.startpoints, arguments.explicit)
        if exitcode != 0:
            exit(exitcode)
    except KeyboardInterrupt:
        exit(3)
