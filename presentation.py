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
import algorithm_abbas

### Main
def exithandler(sig, frame):
    print('Exiting')
    exit(3)

def run(filename, c=(6000, 4500), overwrite=False, plot=False, algorithm=""):
    global convex_hull, points, indices, vertices # make convex_hull algorithm specific

    start_t = HCOMMON.snaptime()
    HDCEL.points = points
    vertices = [HDCEL.Vertex(index=i) for i in range(len(points))]


    '''make sure that only one approach is active when running the program, as they have different terms of sorting'''
    if algorithm == "ben_v1":
        algorithm_ben_v1.run(_vertices=vertices, _origin=HDCEL.Vertex(explicit_x=c[0], explicit_y=c[1]), _verbose=verbose)

    if algorithm == "abbas":
        algorithm_abbas.run(verbose, vertices)
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
        parser.add_argument('-a', '--algorithm', type=str, dest='algorithm', default="ben_v1", choices=["ben_v1", "abbas"], help='choose algorithm to execute')
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
