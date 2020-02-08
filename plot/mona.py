import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys

sys.path.append("../bin")
import HJSON

#points,_ = HJSON.readTestInstance("../instances/uniform/uniform-0002000-1.instance.json")
points,_ = HJSON.readTestInstance("../instances/images/mona-lisa-1000000.instance.json")

for i,p in enumerate(points):
    if i % 2: plt.plot(p[0],p[1],"b.")
plt.savefig("mona-lisa.png")
