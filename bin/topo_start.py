import HJSON
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import Delaunay
import scipy
import numpy as np

# =============================================================================
# setup -----------------------------------------------------------------------
instance_points,instance = HJSON.readTestInstance("../instances/images/euro-night-0000010.instance.json")

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for p in instance_points:
    ax.scatter(p[0], p[1], c="b", marker='.', s=len(instance_points))
# =============================================================================
# triangulation of instance points  -------------------------------------------
t_tri = Delaunay(instance_points)

t_edges = []
for sim in t_tri.simplices: # append all inner edges to t_edges
    for i in range(len(sim)-1):
        t_edges.append([sim[i-1], sim[i]])
for ch in t_tri.convex_hull: # append convex hull to t_edges
    ap = True
    for e in t_edges:
        if (ch[0] == e[0] and ch[1] == e[1]) or (ch[0] == e[1] and ch[1] == e[0]):
            ap = False
    if ap:
        t_edges.append([ch[0],ch[1]])

# =============================================================================
# calculate and draw start points   -------------------------------------------
start_points=[]
for e in t_edges:
    plt.plot((instance_points[e[0]][0], instance_points[e[1]][0]),
            (instance_points[e[0]][1], instance_points[e[1]][1]), "b--")
    X1 = instance_points[e[0]][0]
    X2 = instance_points[e[1]][0]
    Y1 = instance_points[e[0]][1]
    Y2 = instance_points[e[1]][1]
    start_points.append([
        (X1 + X2) / 2,
        (Y1 + Y2) / 2,
        scipy.linalg.norm([X1-X2,Y1-Y2]),
        0 # outgoing s_edges count
        ])

# =============================================================================
# calculate triangulation of starting point graph   ---------------------------
start_points_td = []
for s in start_points:
    start_points_td.append([s[0],s[1]])
s_tri = Delaunay(start_points_td)

s_edges = []
for sim in s_tri.simplices: # append all inner edges to t_edges
    for i in range(len(sim)-1):
        s_edges.append([sim[i-1], sim[i]])
for ch in s_tri.convex_hull: # append convex hull to t_edges
    ap = True
    for e in s_edges:
        if (ch[0] == e[0] and ch[1] == e[1]) or (ch[0] == e[1] and ch[1] == e[0]):
            ap = False
    if ap:
        s_edges.append([ch[0],ch[1]])

# =============================================================================
# calculate metrics for outgoing edges  ---------------------------------------
for e in s_edges: # save point with higher z value in first place
    if start_points[e[0]][2] < start_points[e[1]][2]:
        e[0],e[1] = e[1],e[0]
for e in s_edges: # sum outgoing edges for each starting point
    start_points[e[0]][3] += 1

mi, avg, ma = start_points[0][3], 0, 0
for s in start_points:
    if mi > s[3]: mi = s[3]
    avg += s[3]
    if ma < s[3]: ma = s[3]
avg /= len(start_points)

def f(x,y):
    return np.sin(np.sqrt(x ** 2 + y ** 2))
# =============================================================================
# plot starting point graph ---------------------------------------------------
x,y,z = [],[],[]
for s in start_points:
    x.append(s[0])
    y.append(s[1])
    z.append(s[2])

ax.plot_trisurf(x, y, z, cmap='viridis', edgecolor='none');

"""for e in s_edges: # starting point graph edges
    plt.plot((start_points[e[0]][0], start_points[e[1]][0]),
            (start_points[e[0]][1], start_points[e[1]][1]),
            (start_points[e[0]][2], start_points[e[1]][2]),
            "g-")"""
for s in start_points: # plot altitude of starting points
    plt.plot((s[0], s[0]), (s[1], s[1]), (0, s[2]), "r:")
"""
for p in start_points: # color starting points based on metric
    color = "b"
    if p[3] == mi:
        color="g"
    if p[3] == ma:
        color="r"
    ax.scatter(p[0], p[1], p[2], c=color, marker="o")"""

plt.show()
