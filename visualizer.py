import matplotlib.pyplot as plt
import argparse
import json
import sys

def readInstance(filename):
    points = []
    with open(filename) as json_file:
        data = json.load(json_file)
        for p in data['points']:
            points.append([int(p['x']), int(p['y'])])
        json_file.close()
        return points

def readSolution(filename):
    filename = "solutions/" + filename.split("/",1)[-1] # fix path
    filename = filename.split(".",1)[0] + ".solution.json" # substitute "instance" with "solution"
    try:
        solutionfp = open(filename, 'r')
    except:
        if verbose: print("No solution existing in %s" % filename)
        exit(0)

    data = json.load(solutionfp)
    #comment
    iteration = int(data['meta']['iteration'])
    coord = [int(n) for n in ((data['meta']['coordinates']).strip("() ").split(","))] #
    edge = int(data['meta']['edges'])
    degavg = float(data['meta']['degree_avg'])
    degmax = int(data['meta']['deg_max'])
    edgebetter = int(data['meta']['edges_better'])
    degavgov = float(data['meta']['degree_avg_overall'])
    degmaxov = int(data['meta']['degree_max_overall'])

    edges = []
    for e in data['edges']:
        edges.append([int(e['i']), int(e['j'])])

    solutionfp.close()
    return { 'iteration' : iteration, 'coordinates' : coord, \
             'edges' : edge, 'deg_avg' : degavg, 'deg_max' : degmax, \
             'edges_better' : edgebetter, 'deg_avg_ov' : degavgov, \
             'deg_max_ov' : degmaxov }, edges

def drawPoints(points, edges, meta):
    degree = [0]*len(points)
    for e in edges:
        degree[e[0]] += 1
        degree[e[1]] += 1

    if len(points) > 5000:
        s = "."
    else:
        s = "o"
    for i,p in enumerate(points):
        if degree[i] == 0 or degree[i] == 1:
            c = 'k' #black
        if degree[i] <= meta["deg_avg"]:
            c = 'g' #green
        if degree[i] > meta["deg_avg"]:
            c = 'y' #yellow
        if degree[i] == meta["deg_max"]:
            c = 'r' #red
        plt.plot(p[0], p[1], c+s)
    plt.plot(meta["coordinates"][0],meta["coordinates"][0], "cD")

def drawEdges(points, edges):
    for e in edges:
        plt.plot(
            [points[e[0]][0], points[e[1]][0]],
            [points[e[0]][1], points[e[1]][1]],
            "b-")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bens Algorithm for SoCG')
    parser.add_argument('file')
    arguments = parser.parse_args()
    points = readInstance(arguments.file)
    meta, edges = readSolution(arguments.file)
    drawEdges(points,edges)
    drawPoints(points,edges,meta)
    print("i:\t%i\nedges:\t%i\nbetter:\t%i\navg:\t%.2f\nmax:\t%i\navg_ov:\t%.2f\nmax_ov: %i"
            % (meta['iteration'], meta['edges'], meta['edges_better'], \
               meta['deg_avg'], meta['deg_max'], meta['deg_avg_ov'], meta['deg_max_ov']))
    sys.stdout.flush()
    plt.show()
