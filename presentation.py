"""@package docstring
Software project for the Computational Geometry Week 2020 competition
"""
import sys
import signal
import argparse
import math
from collections import defaultdict

sys.path.append('./bin')
#import HCLUSTER
import HCOMMON
import HDCEL
import HJSON
import HVIS

import algorithm_wave
import algorithm_merged
import algorithm_pass
import algorithm_nested

def exithandler(sig, frame):
    print('Exiting')
    exit(3)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exithandler)
    try:
        # parser --------------------------------------------------------------
        parser = argparse.ArgumentParser(description='Algorithms for SoCG 2020 by students of FU Berlin')
        parser.add_argument('file')
        parser.add_argument('-a', '--algorithm', type=str, dest='algorithm', default="pass",
                            choices=["wave", "merged", "pass", "nested"], help='choose algorithm to execute')
        parser.add_argument('-o', '--overwrite', action='store_true', dest='overwrite', help='Overwrite existing solution if better')
        parser.add_argument('-p', '--plot', action='store_true', dest='plot', help='Show plot - not recommended for large instances')
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Print some information')
        parser.add_argument('-l', '--limit', type=int, nargs=2, dest='limit', help='Don\'t execute if amount of points is outside of limit')
        parser.add_argument('-c', '--coordinates', type=int, nargs=2, dest='coord', help='Set coordinates of start point')
        parser.add_argument('-r', '--random', nargs='?', default=0, dest='rndm', help='Set random seed')
        parser.add_argument('-e', '--explicit', type=int, default=0, dest='explicit', help='Amount of used start points in percent')
        arg = parser.parse_args()

        # init ----------------------------------------------------------------
        global convex_hull, points, indices, vertices # make convex_hull algorithm specific
        HVIS.initVis()

        start_t = HCOMMON.snaptime()
        points,instance = HJSON.readTestInstance(arg.file)
        if arg.limit != None:
            if len(points) < arg.limit[0] or len(points) > arg.limit[1]:
                if arg.verbose: print("Error: outside of limit %d < %d < %d" % (arg.limit[0], len(points), arg.limit[1]))
                exit(2)

        HDCEL.points = points
        vertices = [HDCEL.Vertex(index=i) for i in range(len(points))]

        c = arg.coord
        if arg.coord == None:
            c = HCOMMON.randomstart(points, arg.rndm, arg.verbose)

        # run -----------------------------------------------------------------
        if arg.algorithm == "wave":
            algorithm_wave.run(_vertices=vertices, _origin=HDCEL.Vertex(explicit_x=c[0], explicit_y=c[1]), _verbose=arg.verbose)

        elif arg.algorithm == "merged":
            algorithm_merged.run(_vertices=vertices, _filename=arg.file, _verbose=arg.verbose, _explicit=arg.explicit)

        elif arg.algorithm == "pass":
            algorithm_pass.run(_vertices=vertices, _filename=arg.file, _verbose=arg.verbose, _explicit=arg.explicit)

        elif arg.algorithm == "nested":
            algorithm_nested.run(arg.verbose, vertices)

        # cleanup -------------------------------------------------------------
        edges = HDCEL.get_edge_dict(arg.verbose)
        HCOMMON.snapshoot(start_t, "Computation", arg.verbose)

        written = HJSON.writeTestSolution(arg.file,instance,c,arg.verbose,edges,arg.overwrite,arg.algorithm)

        if arg.plot:
            start_t = HCOMMON.snaptime()
            HVIS.drawEdges(edges,points)
            HVIS.drawPoints(points,edges)
            HCOMMON.snapshoot(start_t, "Plotting", arg.verbose)
            HVIS.show()

        exit(written)
    except KeyboardInterrupt:
        exit(3)
