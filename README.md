## Convex Polygons

This repository contains algorithms and solutions for the CG:SHOP competition 2020.

All Algorithms were created and implemented by Benjamin Kahl, Semjon Kerner, Abbas Mohammed Murrey and Konstantin Jaehne, students of computer scince at Freie Universität Berlin as part of a course by Prof. Günter Rote.

Further explanations will be added as a paper and will be linked here.
You can find our final presentation for the course [here](https://github.com/SemjonKerner/convex_polygons/blob/b5412ddf3189458d07803e934d98bb67e8e7cc36/texinput/convex_polygons.pdf).

The problem stated by this competition (see [CG:SHOP 2020](
https://cgshop.ibr.cs.tu-bs.de/competition/cg-shop-2020/)):  
_Given a set S of n points in the plane. The objective is to compute a plane graph with vertex set S (with each point in S having positive degree) that partitions the convex hull of S into the smallest possible number of convex faces. Note that collinear points are allowed on face boundaries, so all internal angles of a face are at most π_

## Execution

The algorithms are executed with presentation.py

usage: presentation.py [-h] [-a {wave,merged,pass,nested}] [-o] [-p] [-v] [-l LIMIT LIMIT] [-c COORD COORD] [-r [RNDM]] [-e EXPLICIT] file

positional arguments:  
file - path to instance file
  
optional arguments:  
-h, --help : __Show this help message__  
-a {wave,merged,pass,nested}, --algorithm {wave,merged,pass,nested} : __Choose algorithm to execute__  
-o, --overwrite : __Overwrite existing solution if new one is better__  
-p, --plot : __Show plot  - Not recommended for large instances (matplotlib is slow)__  
-v, --verbose : __Print some information__  
-l LIMIT LIMIT, --limit LIMIT LIMIT : __Don't execute if amount of points is outside of limit__  
-c COORD COORD, --coordinates COORD COORD : __Set coordinates of start point__  
-r [RNDM], --random [RNDM] : __Set random seed__  
-e EXPLICIT, --explicit EXPLICIT : __Amount of used start points in percent__  

## About the Algorithms
We developed 4 Algorithms for this competition.
Except from _nested hulls_ they are essentially evolutions of each other.

### Nested Hulls
- Repeatedly creates convex hulls from unconnected vertices from outside to the inside.
- Connects these convex hulls respecting the constraints on convex faces.
- Removes unnecessary edges from the former convex hulls.

This algorithm performs very well on instances with many collinear points.

### Single Convex Waves
- Starting at one (random) point, it iteratively connects the closest point (by euclidean distance to the start point)
- The created graph will allways keep a convex hull after connecting a new point
- A point is connected to the most outer points on the convex hull and all points inbetween on the convex hull (except for points that are collinear on the convex hull)
- Edges between those Points on the convex hull are deleted when the resulting face will be convex

This algorithm was the fastest of all four.

### Merged Convex Waves
We came up with the idea of starting at many start points, because we realized that _Single Convex Wave_ was not very efficient further from the start point, resulting in wave like graphs. Hence the name.
Yet, starting with multiple start points and growing multiple convex hulls brought some unexpected difficulties.
When two convex hulls grew into each other, the algorithm had to merge them to keep the convex hull intact. This merge is very costly in time complexity, code comprehensibility and number of vertices.
This algorithm was the worst in all aspects, but still led us to a better approach.

### Pass Based
- This algorithm creates a polygon at given start points until all points were part of a polygon.
- Choosing start points smartly helped creating bigger polygons first. This was the intended effect.
- In contrast this algorithm does not keep convex hulls intact, leading to some following cleaning passes.
- The convex hull for all points is created.
- Islands, not connected to the convex hull, are detected and connected to the convex hull.
- Non-convex faces are repaired - those with inflex edges.
- Stray points are integrated.
- At last the algorithm tries all edges if they may be deleted, by comparing the angles to the adjacent faces.

This algorithm performed best on most instances. It takes longer than _Nested Hulls_ and _Single Convex Wave_ though.
There is still a known bug in this algorithm, but it happens very seldom and on very large instances.. but since the competition is over, we will probably not maintain this algorithm further or fix any bugs.

### Datastructure DCEL
We used Doubly-Connected Edge List (DCEL) as our main datastructure. It allowed fast traversal on the graph with reasonable overhead.

### Start Points
For _Pass Based_ we calculated a set of start points for each instance. We considered multiple approaches, like clustering with kmeans or heatgrids. Eventually we settled with another approach on Delaunay Triangulation. This approach achieved very good start point distributions.

- A Delaunay triangulation is calculated on all instance points. This leaves us with a set I of edges in a triangulation.
- A second Delaunay triangulation is calculated on the midpoints of edges in I. This triangulation yields a set S of edges.
- The edges in S are ordered by the corresponding edges in I, in a way that the edge in S is directed from the midpoint of the longer edge in I to the midpoint of the shorter edge in I.
- For every midpoint the algorithm counts the outgoing edges in I and sorts the resulting list by the degree.

This approach chooses start points between all instance points in order to eliminate longer edges in a _neighborhood_ of edges. That way bigger polygons shall be created first - not in area size, but in number of vertices. Sadly this algorithm didn't show as much of an effect on _Pass Based_ as hoped.
