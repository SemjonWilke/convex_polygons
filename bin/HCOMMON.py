import time
import random

def pointdegree(edges,points):
    degree = None
    if edges != None:
        degree = [0]*len(points)
        for ein in edges['in']:
            degree[ein] += 1
        for eout in edges['out']:
            degree[eout] += 1
    return degree

def randomstart(points, seed=None, verbose=False):
    random.seed(seed, 2)
    if seed != None:
        if verbose: print("Fixed seed is: %s" % str(seed))
    xmin,ymin = min([p[0] for p in points]),min([p[1] for p in points])
    xmax,ymax = max([p[0] for p in points]),max([p[1] for p in points])
    return (random.randint(ymin, ymax), random.randint(xmin, xmax))

def snapshoot(start_t, msg, verbose=False):
    elp_t = time.process_time() - start_t
    if verbose: print("%s time: %02.0f:%02.0f:%2.2f h" % (msg, elp_t/3600, elp_t/60, elp_t))

def snaptime():
    return time.process_time()
