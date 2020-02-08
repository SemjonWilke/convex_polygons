import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys

sys.path.append("../bin")
import HJSON

points,_ = HJSON.readTestInstance("../instances/uniform/uniform-0000200-1.instance.json")

for p in points:
    plt.plot(p[0],p[1], "b.")
plt.savefig("uni_200_1.png")
