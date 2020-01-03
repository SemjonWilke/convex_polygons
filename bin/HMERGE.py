"""
Merges 2 mutually visible convex hulls under the assumption that no points lie inbetewwen ('Ping-ponging')
Args:   self: Primary Iterator / Hull
        other: Secondary Iterator / Hull
        s_left: Index of left-most vertex on self that is visible from other
        s_right: Index of right-most vertex on self that is visible from other
        o_left: Index of left-most vertex on other that is visible from self
        o_right: Index of right-most vertex on other that is visible from self
For a simple illustration check out this ms-paint: https://i.imgur.com/1KFsk3E.png
Note:   'self.ch_i(x)' is equaivalent to x % len(self.convex_hull)
    and 'self.ch(x)' is equivalent to self.convex_hull[self.ch_i(x)]
"""
def merge_Hulls(self, other, s_left, s_right, o_left, o_right):
    # As a first step we create two lists s and o that contain the chain
    # of vertices that need to be joined on self and other respectively

    # Vertex chain on self into list s:
    s = [self.ch(s_left)]
    i = s_left - 1  # We iterate backwards because we move clockwise
    while self.ch_i(s_right)!=self.ch_i(i):
        s.append(self.ch(i))
        i-=1
    s.append(self.ch(s_right))

    # Vertex chain on other into list o:
    o = [other.ch(o_left)]
    i = o_left + 1  # We iterate forwards because we move counter-clockwise
    while other.ch_i(o_right)!=other.ch_i(i):
        o.append(other.ch(i))
        i+=1
    o.append(other.ch(o_right))

    # Now we have to lists s and o going from left to right.
    # We connect the two left-most vertices, as these need to be connected either way.
    i, j = 0, 0
    s[i].connect_to(o[j])

    # This block of code treats a rare edge-case where a single edge on other can see the entirety of self or vice-versa
    if self.ch_i(s_left)==self.ch_i(s_right) and len(o)<=2:
        i+=1
        s[i].connect_to(o[j])
        print("WARN: Rare edge case during merge.")
    elif other.ch_i(o_left)==other.ch_i(o_right) and len(s)<=2:
        j+=1
        s[i].connect_to(o[j])
        print("WARN: Rare edge case during merge.")

    # Advance i (self) if possible, otherwise j (other) and connect at each step.
    while 1:
        if i+1<len(s) and not self.intersects(s[i+1], o[j]) and not other.intersects(s[i+1], o[j]):
            i+=1
            s[i].connect_to(o[j])
        if j+1<len(o) and not self.intersects(s[i], o[j+1]) and not other.intersects(s[i], o[j+1]):
            j+=1
            s[i].connect_to(o[j])
        if i>=len(s)-1 and j>=len(o)-1:
            break
