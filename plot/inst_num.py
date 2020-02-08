import csv
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 18})

fig, ax = plt.subplots()

plt.ylabel('#points')

ben_v1=[0,0]
abbas=[0,0]
ben_v3=[0,0]
with open('rank.csv', 'r') as fp:
    reader = csv.reader(fp)
    for row in reader:
        if int(row[-1]) == 1: #v1
            ben_v1[0] += 1
            ben_v1[1] += int(row[1])
        elif int(row[-1]) == 2: #abbas
            abbas[0] += 1
            abbas[1] += int(row[1])
        elif int(row[-1]) == 3: #v3
            ben_v3[0] += 1
            ben_v3[1] += int(row[1])
a=ben_v1[0]+abbas[0]+ben_v3[0]

#plt.bar(ben_v1[0]/2,ben_v1[1],ben_v1[0],edgecolor="b", color="w", linewidth=5, label="wave")
#plt.bar((ben_v1[0])+abbas[0]/2,abbas[1],abbas[0],edgecolor="y", color="w", linewidth=5,label="nested")
#plt.bar(((ben_v1[0])+abbas[0])+ben_v3[0]/2,ben_v3[1],ben_v3[0],edgecolor="r", color="w", linewidth=5,label="pass")
labels = ["single convex wave", "nested hulls", "pass based"]
plt.bar(1,ben_v1[1], color="b", label=labels[0])
plt.bar(2,abbas[1], color="y", label=labels[1])
plt.bar(3,ben_v3[1], color="r", label=labels[2])
ax.set_xticks([1,2,3])
ax.set_xticklabels(labels)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels)
plt.show()
