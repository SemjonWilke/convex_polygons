import glob
import csv
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 18})

fig, ax = plt.subplots()
ax.set_xscale('log')

ax.set_ylim([0.24,0.67])

plt.ylabel('score')
plt.xlabel('#points')

wave=[[],[]]
nested=[[],[]]
passbased=[[],[]]
with open('rank.csv', 'r') as fp:
    reader = csv.reader(fp)
    for row in reader:
        if "ortho" in row[0] or "rop" in row[0]:
            continue
            m="p"
        else:
            m="+"
        if int(row[-1]) == 1: #v1
            #wave[0].append(int(row[1]))
            #wave[1].append(float(row[-2]))
            a,=plt.plot(int(row[1]),float(row[-2]),"b"+m, label="single convex wave")
        elif int(row[-1]) == 2: #nested
            #nested[0].append(int(row[1]))
            #nested[1].append(float(row[-2]))
            if m == "+":
                b,=plt.plot(int(row[1]),float(row[-2]),"y"+m, label="nested hulls")
            else:
                plt.plot(int(row[1]),float(row[-2]),"y"+m, label="nested hulls")
        elif int(row[-1]) == 3: #v3
            #passbased[0].append(int(row[1]))
            #passbased[1].append(float(row[-2]))
            c,=plt.plot(int(row[1]),float(row[-2]),"r"+m, label="pass based")
#"""
plt.plot([0,1000000], [0.3726332959,0.3726332959], "b--", alpha=0.3)
plt.plot([0,1000000], [0.3810439757,0.3810439757], "y--", alpha=0.3)
plt.plot([0,1000000], [0.4097391527,0.4097391527], "r--", alpha=0.3)
plt.text(1000000, 0.366, 'average', color="y", alpha=0.3, horizontalalignment="right", backgroundcolor="w")
plt.text(1000000, 0.357, 'average', color="b", alpha=0.3, horizontalalignment="right")
plt.text(1000000, 0.394, 'average', color="r", alpha=0.3, horizontalalignment="right")
"""
plt.plot([0,1000000], [0.3790039879,0.3790039879], "b--", alpha=0.3)
plt.text(1000000, 0.364, 'average', color="b", alpha=0.3, horizontalalignment="right")
plt.plot([0,1000000], [0.5838459889,0.5838459889], "y--", alpha=0.3)
plt.text(1000000, 0.568, 'average', color="y", alpha=0.3, horizontalalignment="right")
plt.plot([0,1000000], [0.4441575996,0.4441575996], "r--", alpha=0.3)
plt.text(1000000, 0.429, 'average', color="r", alpha=0.3, horizontalalignment="right")
#"""

#plt.plot(wave[0],wave[1],"b.", label="wave")
#plt.plot(nested[0],nested[1],"y.",label="nested")
#plt.plot(passbased[0],passbased[1],"r.",label="passbased")
#handles, labels = ax.get_legend_handles_labels()
l = ax.legend(handles=[a,b,c])
plt.show()
