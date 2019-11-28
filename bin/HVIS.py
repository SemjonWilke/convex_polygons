import matplotlib.pyplot as plt

import HCOMMON

fig=None
axs=None

def col(color, degree, point, index):
    #if kmeans != None: # TODO get kmeans from hcluster
    #    return kcol[kmeans.predict([point])[0]]
    if degree == None:
        return color
    if degree[index] == 0 or degree[index] == 1:
        return 'w' #white
    if degree[index] == 2:
        return 'g' #green
    if degree[index] == 3:
        return 'y' #yellow
    if degree[index] >= 4:
    #    return 'c' #cyan
    #if degree[index] == 5:
    #    return 'm' #magenta
    #if degree[index] >= 6:
        return 'r' #red

def drawPoints(points, edges=None, color='r'):
    """ draws points to plt
    input:      points as dictionary of lists 'x' and 'y'
                color of points (matplotlib style)
    """
    degree = HCOMMON.pointdegree(edges,points)
    for i,val in enumerate(points):
        axs[0].plot(val[0], val[1], color=col(color,degree,val,i), marker='o')
    """if kmeans != None:
        for i,c in enumerate(kmeans.cluster_centers_):
            axs[0].plot(c[0], c[1], color='k', marker='o')
            axs[0].plot(c[0], c[1], color=kcol[i], marker='P') """# TODO get kcol from kmeans in HCLUSTER

def drawEdges(edges, points, color='b-'):
    """ draws edges to plt
    input:      list of edges indexing points
                points as dictionary of lists 'x' and 'y'
                color of edges (matplotlib style)
    """
    #if kmeans == None: # TODO get kmeans from hcluster
    for index,val in enumerate(edges['in']):
        i = edges['in'][index]
        j = edges['out'][index]
        axs[0].plot(
            [points[i][0], points[j][0]],
            [points[i][1], points[j][1]],
            color
        )

def drawHull():
    for i in range(len(convex_hull)):
        axs[0].plot([ch(i).x(), ch(i+1).x()], [ch(i).y(), ch(i+1).y()], 'r-')

def drawSingleEdge(e, color='b'):
    axs[0].plot([e.origin.x(), e.nxt.origin.x()], [e.origin.y(), e.nxt.origin.y()], color+'-')

def drawSingleHEdge(inp, outp, color='b'):
    axs[0].plot([points[inp][0], points[outp][0]], [points[inp][1], points[outp][1]], color+'-')

def drawSinglePoint(v):
    axs[0].plot(v.x(), v.y(), 'ks')

def initVis():
    global fig
    global axs
    fig,axs = plt.subplots(2)
    return fig,axs

def show():
    plt.show()

#TODO: reuse branch solution drawing functions
"""
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
"""
