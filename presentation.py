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
        return [x,y,index], instance

def writetestsolution(filename, instance, edges=[]):
    data = {
        'type':'Solution',
        'instance_name' : instance,
        'meta' : {'comment':''},
        'edges' : []
    }
    for edge in edges:
        data['edges'].append({
            'i': str(edge[0][2]),
            'j': str(edge[1][2]),
        })

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def drawpoints(points, color='r.'):
    for i in range(len(points[0])):
        plt.plot(points[0][i],points[1][i], color)

def drawedges(edges, color='b-'):
    for edge in edges:
        plt.plot((edge[0][0], edge[0][1]),(edge[1][0],edge[1][1]), color)

if __name__ == '__main__':
    points,instance = readtestinstance('euro-night-0000100.instance.json')
    drawpoints(points)
    #drawedges(edges)
    writetestsolution('euro-night-0000100.solution.json',instance)
    plt.show()
