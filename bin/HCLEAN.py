import HDCEL

def isLeftOf(a, b, v):
    return ((b.x() - a.x())*(v.y() - a.y()) - (b.y() - a.y())*(v.x() - a.x())) > 0

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

    print("Removed " + str(c) + " superfluous edges...")
