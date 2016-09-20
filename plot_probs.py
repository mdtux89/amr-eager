import numpy as np
import matplotlib.pylab as pyl
import matplotlib.pyplot as plt
labels_y = open("resources/relations.txt").read().splitlines()
labels_x = open("resources/dependencies.txt").read().splitlines()
labels_x.extend([item+"INV" for item in open("resources/dependencies.txt").read().splitlines()])

def plot(cm, title='p(amr/dep)', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks_x = np.arange(len(labels_x))
  tick_marks_y = np.arange(len(labels_y))
    plt.xticks(tick_marks_x, labels_x, rotation=90)
    plt.yticks(tick_marks_y, labels_y)
    plt.tight_layout()
    plt.ylabel('AMR Relation')
    plt.xlabel('Dependency')

nrels = 71
ndeps = 90
a = np.empty((nrels,ndeps))
for i in range(0,nrels):
        for j in range(0,ndeps):
                a[i,j] = 0
for line in open("GIVENDEP2.txt"):
        deplabel,amrlabel,p = line.split()
        a[amrlabel,deplabel] = p
plot(a)
plt.show()

