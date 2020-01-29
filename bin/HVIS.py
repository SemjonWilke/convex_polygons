import matplotlib
matplotlib.use("Agg")
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

import HCOMMON

fig=None
axs=None

def col(color, degree, point, index):
    if degree == None:
        return color
    if degree[index] == 0 or degree[index] == 1:
        return 'k' #white
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
        axs.plot(val[0], val[1], color=col(color,degree,val,i), marker='o')

def drawEdges(edges, points, color='b-'):
    """ draws edges to plt
    input:      list of edges indexing points
                points as dictionary of lists 'x' and 'y'
                color of edges (matplotlib style)
    """
    for index,val in enumerate(edges['in']):
        i = edges['in'][index]
        j = edges['out'][index]
        axs.plot(
            [points[i][0], points[j][0]],
            [points[i][1], points[j][1]],
            color
        )

def drawHull():
    for i in range(len(convex_hull)):
        axs.plot([ch(i).x, ch(i+1).x], [ch(i).y, ch(i+1).y], 'r-')

def drawSingleEdge(e, color='b', width=4):
    axs.plot([e.origin.x, e.nxt.origin.x], [e.origin.y, e.nxt.origin.y], color+'-', linewidth=width)

def drawSingleTEdge(p1, p2, color='b', width=4):
    axs.plot([p1.x, p2.x], [p1.y, p2.y], color+'-', linewidth=width)

def drawVector(v, origin=None, color='k', width=2):
    if origin is None: axs[0].plot([0, v.x], [0, v.y], color+'-', linewidth=width)
    else: axs.plot([origin.x, origin.x+v.x], [origin.y, origin.y+v.y], color+'-', linewidth=width)

def drawSingleHEdge(inp, outp, points, color='b'):
    axs.plot([points[inp][0], points[outp][0]], [points[inp][1], points[outp][1]], color+'-')

def drawSinglePoint(v):
    axs.plot(v.x, v.y, 'ks')

def drawSingleHPoint(p, c='ks'):
    axs.plot(p[0], p[1], c)

def initVis():
    global fig
    global axs
    fig,axs = plt.subplots(1)
    return fig,axs

def show():
    #plt.show()
    plt.savefig("abc.png")

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
