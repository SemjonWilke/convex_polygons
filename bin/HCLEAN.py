import HDCEL
import HVIS

verbose = False

def isLeftOf(a, b, v):
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) > 0

def segment_intersect(l1, l2, g1, g2):
    if len(set([l1,l2,g1,g2]))!=len([l1,l2,g1,g2]): return False
    return isLeftOf(l1, l2, g1) != isLeftOf(l1, l2, g2) and isLeftOf(g1, g2, l1) != isLeftOf(g1, g2, l2)

def dupes(listOfElems):
    ''' Check if given list contains any duplicates '''
    if len(listOfElems) == len(set(listOfElems)):
        return False
    else:
        return True

def clean_edges():
    c = 0
    edges = HDCEL.get_edge_list()

    redundant_edges = []
    for e in edges:
        p1 = e.twin.prev.origin
        p2 = e.nxt.origin
        p3 = e.nxt.nxt.origin

        q1 = e.prev.origin
        q2 = e.origin
        q3 = e.twin.nxt.nxt.origin

        if not dupes([p1,p2,p3,e.origin]) and not isLeftOf(p1, p2, p3) and not dupes([q1,q2,q3,e.twin.origin]) and not isLeftOf(q1, q2, q3):
            e.remove()
            c += 1

    if verbose: print("Removed " + str(c) + " superfluous edges...")

def check_cross():
    edges = HDCEL.get_edge_list()
    for i in range(len(edges)):
        for j in range(i, len(edges)):
            if segment_intersect(edges[i].origin, edges[i].nxt.origin, edges[j].origin, edges[j].nxt.origin):
                if verbose: print("WARN: DETECTED CROSSING EDGES!")
                HVIS.drawSingleEdge(edges[i], color="r", width=4)
                HVIS.drawSingleEdge(edges[j], color="r", width=4)
                return True
    return False
