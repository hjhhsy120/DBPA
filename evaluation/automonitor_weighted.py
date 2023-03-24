from cmath import sqrt
import pickle
from typing import Counter
from scipy.spatial import distance
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import argparse

faultlist = ['fault1', 'fault2', 'fault3', 'fault4', 'fault5', 'stress', 'lockwait', 'setknob', 'multiindex']

parser = argparse.ArgumentParser(description='Arguments from CMD')
parser.add_argument('--test_size', type=float, default=0.4, help='test_size')
parser.add_argument('--K', type=int, default=10, help='K')
args = parser.parse_args()
test_size = args.test_size
K = args.K

with open('data_use_autom.pkl', 'rb') as f:
    V, labels = pickle.load(f)

faultnum = 1024
faultcnt = {}
faultinterval = dict(Counter(labels))
for key in faultinterval:
    faultinterval[key] = int(faultinterval[key]/faultnum)
    faultinterval[key] = max(1, faultinterval[key])
newV = []
newlabels = []
for i in range(len(V)):
    if not labels[i] in faultcnt:
        faultcnt[labels[i]] = 0
    if faultcnt[labels[i]] % faultinterval[labels[i]] == 0:
        newV.append(V[i])
        newlabels.append(labels[i])
    faultcnt[labels[i]] += 1
V = np.array(newV)
labels = np.array(newlabels)
trainfea, testfea, trainlab, testlab = train_test_split(
    V, labels, stratify=labels, test_size=test_size, random_state=42)



faultweight = {}
maxfaultcnt = faultcnt[max(faultcnt, key=lambda x: faultcnt[x])]
for key in faultcnt:
    faultweight[key] = maxfaultcnt / faultcnt[key]

V_aggr = []
V_dict = {}
for i in range(len(trainfea)):
    if not trainlab[i] in V_dict:
        V_dict[trainlab[i]] = []
    V_dict[trainlab[i]].append(trainfea[i])
faultnames = list(V_dict.keys())
for fault in faultnames:
    V_aggr.append(np.mean(V_dict[fault], axis=0))  

A = {}
for i in range(len(faultnames)):
    G = np.zeros_like(V_aggr[i])
    N = 0
    for j in range(len(faultnames)):
        if i != j:
            beta = 1/(distance.euclidean(V_aggr[i], V_aggr[j]))**2
            N += beta
            G += beta * V_aggr[j]
    G = G / N
    Res = np.abs(G - V_aggr[i])
    N = np.linalg.norm(Res, ord=1)
    A[faultnames[i]] = Res/N


def weightedDis(a, b, weight):
    dis = 0.0
    for i in range(len(a)):
        dis += weight[i]*(a[i]-b[i])**2
    dis = sqrt(dis)
    return dis


acc = 0.0
predlab = []
for i in range(len(testfea)):
    distances = []
    counter = {}
    for j in range(len(trainfea)):
        distances.append(weightedDis(testfea[i], trainfea[j], A[trainlab[j]]))
    sortDistance = np.array(distances).argsort()
    for k in range(K):
        vote = trainlab[sortDistance[k]]
        counter[vote] = counter.get(
            vote, 0) + min(K-sum(counter.values()), faultweight[vote])
        if sum(counter.values()) == K:
            break
    pred = max(counter, key=lambda x: counter[x])
    predlab.append(pred)
    if pred == testlab[i]:
        acc += 1

acc /= len(testfea)
print('{:<10}\tAcc = {:.4f}'.format('AutoM',acc))
results = precision_recall_fscore_support(
    testlab, predlab, labels=faultlist, average=None)
for j in range(9):
    print('{:<10}\t{:.4f},{:.4f},{:.4f}'.format(faultlist[j], results[0][j], results[1][j], results[2][j]))

clf = KNeighborsClassifier(n_neighbors=K)
clf.fit(trainfea, trainlab)
predlab = clf.predict(testfea)
print('{:<10}\tAcc = {:.4f}'.format('KNN',accuracy_score(testlab, predlab)))
results = precision_recall_fscore_support(
    testlab, predlab, labels=faultlist, average=None)
for j in range(9):
    print('{:<10}\t{:.4f},{:.4f},{:.4f}'.format(faultlist[j], results[0][j], results[1][j], results[2][j]))
