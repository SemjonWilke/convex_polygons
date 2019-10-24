"""@package docstring
Software project for the Computational Geometry Week 2020 competition
"""

import matplotlib.pyplot as plt
import json

def readtestinstance(filename):
    """ reads a test instance file by name
    input:      filename as string
    returns:    points as dictionary of lists 'x' and 'y'
                instance name as string
    """
    points = {'x': [], 'y': []}
    with open(filename) as json_file:
        data = json.load(json_file)
        for p in data['points']:
            points['x'].append(int(p['x']))
            points['y'].append(int(p['y']))
            # print('%i: (%.1f | %.1f)' % (int(p['i']), float(p['x']), float(p['y'])))
        instance = data['name']
        return points, instance

def writetestsolution(filename, instance, edges=[]):
    """ writes edges to a solution file
    input:      filename as string
                instance name as string
                list of edges by indices of points
    """
    data = {
        'type':'Solution',
        'instance_name' : instance,
        'meta' : {'comment':''},
        'edges' : []
    }
    for edge in edges:
        data['edges'].append({
            'i': str(edge['in']),
            'j': str(edge['out']),
        })

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def drawpoints(points, color='r.'):
    """ draws points to plt
    input:      points as dictionary of lists 'x' and 'y'
                color of points (matplotlib style)
    """
    for i,val in enumerate(points['x']):
        plt.plot(points['x'][i], points['y'][i], color)

def drawedges(edges, points, color='b-'):
    """ draws edges to plt
    input:      list of edges indexing points
                points as dictionary of lists 'x' and 'y'
                color of edges (matplotlib style)
    """
    for index,val in enumerate(edges['in']):
        i = edges['in'][index]
        j = edges['out'][index]
        plt.plot(
            [points['x'][i], points['x'][j]],
            [points['y'][i], points['y'][j]],
            color
        )

if __name__ == '__main__':
    points,instance = readtestinstance('euro-night-0000100.instance.json')
    drawpoints(points)
    #''' delete # to switch comments and have an example
    edges = {'in' : [], 'out' : []}
    '''
    edges = {'in' : [1,3,5,7,9], 'out' : [0,2,4,6,8]} # example
    #'''
    drawedges(edges,points)
    writetestsolution('euro-night-0000100.solution.json',instance)
    plt.show()
