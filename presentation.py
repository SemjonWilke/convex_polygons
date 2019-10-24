import matplotlib.pyplot as plt
import json

def readtestinstance(filename):
    x = []
    y = []
    with open('euro-night-0000100.instance.json') as json_file:
        data = json.load(json_file)
        for p in data['points']:
            x.append(int(p['x']))
            y.append(int(p['y']))
            # print('%i: (%.1f | %.1f)' % (int(p['i']), float(p['x']), float(p['y'])))
        return [x,y]

def writetestresult(filename):
    return

def drawpoints(points, color='r.'):
    for i in range(len(points[0])):
        plt.plot(points[0][i],points[1][i], color)

def drawedges(edges, color='b-'):
    for edge in edges:
        plt.plot((edge[0][0], edge[0][1]),(edge[1][0],edge[1][1]), color)

if __name__ == '__main__':
    points = readtestinstance('euro-night-0000100.instance.json')
    drawpoints(points)
    #drawedges(edges)
    #writetestresult()
    plt.show()
