import matplotlib.pyplot as plt
import json

def readtestinstance(filename):
    x = []
    y = []
    index = []
    with open(filename) as json_file:
        data = json.load(json_file)
        for p in data['points']:
            x.append(int(p['x']))
            y.append(int(p['y']))
            index.append(int(p['i']))
            # print('%i: (%.1f | %.1f)' % (int(p['i']), float(p['x']), float(p['y'])))
        instance = data['name']
        return {'x': x, 'y': y, 'index' : index}, instance

def writetestsolution(filename, instance, edges=[]):
    data = {
        'type':'Solution',
        'instance_name' : instance,
        'meta' : {'comment':''},
        'edges' : []
    }
    for edge in edges:
        data['edges'].append({
            'i': str(edge['in']['index']),
            'j': str(edge['out']['index']),
        })

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def drawpoints(points, color='r.'):
    for i in range(len(points['x'])):
        plt.plot(points['x'][i], points['y'][i], color)

def drawedges(edges, color='b-'):
    for edge in edges:
        plt.plot((edge['in']['x'], edge['in']['y']),(edge['out']['x'],edge['out']['y']), color)

if __name__ == '__main__':
    points,instance = readtestinstance('euro-night-0000100.instance.json')
    drawpoints(points)
    edges = { 'in' : {'x', 'y', 'index'}, 'out' :  {'x', 'y', 'index'}} #TODO x,y needn't be duplicated
    drawedges(edges = [])  #TODO edges is empty
    writetestsolution('euro-night-0000100.solution.json',instance)
    plt.show()
