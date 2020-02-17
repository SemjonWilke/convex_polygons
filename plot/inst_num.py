import csv
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 18})

fig, ax = plt.subplots()

plt.ylabel('#points')

wave=[0,0]
nested=[0,0]
passbased=[0,0]
with open('rank.csv', 'r') as fp:
    reader = csv.reader(fp)
    for row in reader:
        if int(row[-1]) == 1: #v1
            wave[0] += 1
            wave[1] += int(row[1])
        elif int(row[-1]) == 2: #nested
            nested[0] += 1
            nested[1] += int(row[1])
        elif int(row[-1]) == 3: #v3
            passbased[0] += 1
            passbased[1] += int(row[1])
a=wave[0]+nested[0]+passbased[0]

#plt.bar(wave[0]/2,wave[1],wave[0],edgecolor="b", color="w", linewidth=5, label="wave")
#plt.bar((wave[0])+nested[0]/2,nested[1],nested[0],edgecolor="y", color="w", linewidth=5,label="nested")
#plt.bar(((wave[0])+nested[0])+pass[0]/2,pass[1],pass[0],edgecolor="r", color="w", linewidth=5,label="pass")
labels = ["single convex wave", "nested hulls", "pass based"]
plt.bar(1,wave[1], color="b", label=labels[0])
plt.bar(2,nested[1], color="y", label=labels[1])
plt.bar(3,passbased[1], color="r", label=labels[2])
ax.set_xticks([1,2,3])
ax.set_xticklabels(labels)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels)
plt.show()
