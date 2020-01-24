# Load an instance
from cgshop2020_pyutils import Instance, Point, Edge, Solution, SolutionChecker
import argparse
import json
from scipy.spatial import ConvexHull #TODO maybe pass the convex hull via solution files
import HVIS

# load challenge instances
def readInstance(filename):
    points = []
    with open(filename) as json_file:
        data = json.load(json_file)
        name = data['name']
        instance = Instance(name=name)

        for p in data['points']:
            instance.add_point(Point(p['x'], p['y']))
        json_file.close()
        return instance, name, data['points']

def readSolution(filename, name):
    filename = "solutions/" + filename.split("/",1)[-1] # fix path
    filename = filename.split(".",1)[0] + ".solution.json" # substitute "instance" with "solution"
    try:
        solutionfp = open(filename, 'r')
    except:
        exit(1)

    solution = Solution(instance=name)

    data = json.load(solutionfp)
    for edge in data['edges']:
        solution.add_edge(Edge(edge['i'], edge['j']))

    solutionfp.close()
    return solution, data['edges']

def score(edges, points):
    p = []
    for point in points:
        p.append((point['x'],point['y']))
    en = len(edges)
    pn = len(p)
    fn = 1 + en - pn
    cn = len(ConvexHull(p).vertices)
    return fn / ((2 * pn) - cn - 2)

def writeCheck(filename, status, points):
    filename = "solutions/" + filename.split("/",1)[-1] # fix path
    filename = filename.split(".",1)[0] + ".solution.json" # substitute "instance" with "solution"
    try:
        json_file = open(filename, 'r')
        data = json.load(json_file)
        json_file.close()
    except:
        exit(1)

    data['meta']['checker_feasible'] = str(status.is_feasible())
    data['meta']['checker_msg'] = str(status.get_message())
    data['meta']['checker_obj_val'] = str(status.get_objective_value())
    data['meta']['score'] = str(score(data['edges'],points))

    json_file = open(filename, 'w')
    json.dump(data, json_file, indent=1)
    json_file.close()

def liveChecker(points, edges, name):
    checker = SolutionChecker()
    inst = Instance(name=name)
    for p in points:
        inst.add_point(Point(p[0], p[1]))

    sol = Solution(instance=name)
    for i,e in enumerate(edges['in']):
        sol.add_edge(Edge(edges['in'][i], edges['out'][i]))

    return checker(instance=inst, solution=sol)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bens Algorithm for SoCG')
    parser.add_argument('file')
    parser.add_argument('-p', '--plot', action='store_true', dest='plot', help='Show plot')
    arguments = parser.parse_args()

    checker = SolutionChecker()
    instance,name,points = readInstance(arguments.file)
    solution,edges = readSolution(arguments.file, name)

    status = checker(instance=instance, solution=solution)
    writeCheck(arguments.file, status, points)

    print(status.get_message())
    if (arguments.plot):
        HVIS.initVis()
        es = {"in":[],"out":[]}
        for e in edges:
            es["in"].append(int(e["i"]))
            es["out"].append(int(e["j"]))
        ps = []

        for p in points:
            ps.append([p["x"], p["y"]])

        HVIS.drawEdges(es,ps)
        HVIS.drawPoints(ps)
        HVIS.show()
