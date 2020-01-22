import json

import HCOMMON

points = []
verbose = True

def getmeta(filename, edges, coord, alg):

    degrees = HCOMMON.pointdegree(edges,points)

    noclose = True
    iteration = 0
    edgenum = len(edges['in'])
    degavg = sum(degrees)/len(degrees)
    degmax = max(degrees)
    edgenumbetter = 0
    degavgov = degavg
    degmaxov = degmax
    checker_feasible = True
    try:
        solutionfp = open(filename, 'r')
    except:
        if verbose: print("No previous solution existing in %s" % filename)
        noclose = False

    if noclose:
        data = json.load(solutionfp)
        try: iteration = int(data['meta']['iteration']) + 1
        except: pass
        try: edgenumbetter = int(data['meta']['edges']) - edgenum
        except: pass
        try: degavgov = float(data['meta']['degree_avg_overall']) + degavg
        except: pass
        try: degmaxov = max(int(data['meta']['degree_max_overall']), degmaxov)
        except: pass
        try: cf = ("True" == data['meta']['checker_feasible'])
        except: cf = True
        solutionfp.close()
    return cf, \
           { 'comment' : "Solution by Students of FU Berlin", 'iteration' : str(iteration),
             'coordinates' : str(coord), 'edges' : str(edgenum), 'degree_avg' : str(degavg),
             'deg_max' : str(degmax), 'edges_better' : str(edgenumbetter),
             'degree_avg_overall' : str(degavgov), 'degree_max_overall' : str(degmaxov),
             'algorithm' : alg, 'authors': ["Konstantin Jaehne", "Benjamin Kahl",
                                            "Semjon Kerner", "Abbas Mohammed Murrey"]}

def writeTestSolution(filename, instance, coord, edges=[], overwrite=False, algorithm="ben_v1"):
    """ writes edges to a solution file
    input:      filename as string
                instance name as string
                list of edges by indices of points
    """

    filename = "solutions/" + filename.split("/",1)[-1] # fix path
    filename = filename.split(".",1)[0] + ".solution.json" # substitute "instance" with "solution"
    cf, meta = getmeta(filename, edges, coord, algorithm)
    better = int(meta['edges_better'])

    try:
        if (not cf): # if old solution is worse, overwrite
            print("works?")
            better = 1
    except: pass

    fexist = True
    try:
        fp = open(filename, 'r')
        fp.close()
    except:
        fexist = False

    if better > 0: # overwrite if its better else discard
        if verbose: print("Found a stronger solution by %s edges" % better)

    data = {
        'type':'Solution',
        'instance_name' : instance,
        'meta' : meta,
        'edges' : []
    }

    for index,val in enumerate(edges['in']):
        data['edges'].append({
            'i': str(edges['in'][index]),
            'j': str(edges['out'][index]),}
        )

    if not fexist or (fexist and better > 0 and overwrite):
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=1)
        if verbose: print("Solution written to %s" % (filename))
        return 0
    if fexist and better <= 0:
        if verbose: print("Solution was weaker by %s edges" % abs(better))
        return 1

def readStartPoints(filename):
    """ reads a startpoints file by name
    input:      filename as string
    returns:    points as array of coordinates
    """
    spoints = []
    with open(filename) as json_file:
        data = json.load(json_file)
        for p in data['points']:
            spoints.append([int(p['x']), int(p['y'])]) # TODO does not work for float
        json_file.close()
        return spoints

def readTestInstance(filename):
    """ reads a test instance file by name
    input:      filename as string
    returns:    points as array of coordinates
                instance name as string
    """
    global points
    with open(filename) as json_file:
        data = json.load(json_file)
        for p in data['points']:
            points.append([float(p['x']), float(p['y'])]) # TODO does not work for float
        instance = data['name']
        json_file.close()
        return points, instance
