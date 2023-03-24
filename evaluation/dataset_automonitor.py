import pickle
from scipy.stats import ks_2samp
import math
import numpy as np
foldernamelist = ['./data/32_128/single/', './data/32_256/single/',
                  './data/64_128/single/', './data/64_256/single/']
# fault1 fault5
faultlist = ['fault1', 'fault2', 'fault3', 'fault4',
             'fault5', 'stress', 'lockwait', 'setknob', 'multiindex']


def getV1(foldername, faultname):
    f = open(foldername + faultname + '_data.pickle', 'rb')
    faultdata = pickle.load(f)
    f.close()
    fealen = len(faultdata[0][0][0])-1
    V = []
    labels = []
    i = 0
    while i < len(faultdata):
        for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
            for nclient in [50, 100, 150]:
                v = []
                for m in range(fealen):
                    faultfea = []
                    for expid in range(3):
                        d = faultdata[i+expid]
                        fea = d[0][d[1][0]:d[1][1]]
                        fea = [f[m+1] for f in fea]
                        faultfea += fea
                    if len(faultfea) > 60:
                        print("V1 too long")
                    normalfea1 = []
                    ndata = normaldata[bench][:math.ceil(len(faultfea)/10)]
                    for nd in ndata:
                        fea = nd[0]
                        fea = [f[m+1] for f in fea]
                        normalfea1 += fea
                    normalfea2 = []
                    ndata = normaldata[bench][len(ndata):2*len(ndata)]
                    for nd in ndata:
                        fea = nd[0]
                        fea = [f[m+1] for f in fea]
                        normalfea2 += fea
                    v.append(ks_2samp(normalfea2, faultfea)[
                             0]-ks_2samp(normalfea1, normalfea2)[0])
                    # print(ks_2samp(normalfea1,normalfea2))
                    # print(ks_2samp(normalfea2,faultfea))
                i += 3
                V.append(v)
                labels.append(faultname)
    print(faultname + ": " + str(len(V)))
    # V = np.array(V)
    # V = V.mean(axis=0)
    # print(V)
    return V, labels

# fault2 fault4


def getV2(foldername, faultname):
    f = open(foldername + faultname + '_data.pickle', 'rb')
    faultdata = pickle.load(f)
    f.close()
    fealen = len(faultdata[0][0][0])-1
    V = []
    labels = []
    i = 0
    while i < len(faultdata):
        for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
            for nclient in [5, 10]:
                v = []
                for m in range(fealen):
                    faultfea = []
                    for expid in range(3):
                        d = faultdata[i+expid]
                        fea = d[0][d[1][0]:d[1][1]]
                        fea = [f[m+1] for f in fea]
                        faultfea += fea
                    if len(faultfea) > 40:
                        print("V2 too long")
                    normalfea1 = []
                    ndata = normaldata[bench][:math.ceil(len(faultfea)/10)]
                    for nd in ndata:
                        fea = nd[0]
                        fea = [f[m+1] for f in fea]
                        normalfea1 += fea
                    normalfea2 = []
                    ndata = normaldata[bench][len(ndata):2*len(ndata)]
                    for nd in ndata:
                        fea = nd[0]
                        fea = [f[m+1] for f in fea]
                        normalfea2 += fea
                    v.append(ks_2samp(normalfea2, faultfea)[
                             0]-ks_2samp(normalfea1, normalfea2)[0])
                    # print(ks_2samp(normalfea1,normalfea2))
                    # print(ks_2samp(normalfea2,faultfea))
                i += 3
                V.append(v)
                labels.append(faultname)
    print(faultname + ": " + str(len(V)))
    # V = np.array(V)
    # V = V.mean(axis=0)
    # print(V)
    return V, labels

# fault3


def getV3(foldername, faultname):
    propcnt = [7, 4, 1, 6]
    cnt = 0
    f = open(foldername + faultname + '_data.pickle', 'rb')
    faultdata = pickle.load(f)
    f.close()
    fealen = len(faultdata[0][0][0])-1
    V = []
    labels = []
    i = 0
    while i < len(faultdata):
        for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
            for nclient in [64, 128]:
                for prop in range(propcnt[cnt]):
                    v = []
                    for m in range(fealen):
                        faultfea = []
                        for expid in range(5):
                            d = faultdata[i+expid]
                            fea = d[0][d[1][0]:d[1][1]]
                            fea = [f[m+1] for f in fea]
                            faultfea += fea
                        if len(faultfea) > 90:
                            print("V3 too long")
                        normalfea1 = []
                        ndata = normaldata[bench][:math.ceil(len(faultfea)/10)]
                        for nd in ndata:
                            fea = nd[0]
                            fea = [f[m+1] for f in fea]
                            normalfea1 += fea
                        normalfea2 = []
                        ndata = normaldata[bench][len(ndata):2*len(ndata)]
                        for nd in ndata:
                            fea = nd[0]
                            fea = [f[m+1] for f in fea]
                            normalfea2 += fea
                        v.append(ks_2samp(normalfea2, faultfea)[
                                 0]-ks_2samp(normalfea1, normalfea2)[0])
                        # print(ks_2samp(normalfea1,normalfea2))
                        # print(ks_2samp(normalfea2,faultfea))
                    i += 5
                    V.append(v)
                    labels.append(faultname)
            cnt += 1
    print(faultname + ": " + str(len(V)))
    # V = np.array(V)
    # V = V.mean(axis=0)
    # print(V)
    return V, labels


# stress
def getV4(foldername, faultname):
    f = open(foldername + faultname + '_data.pickle', 'rb')
    faultdata = pickle.load(f)
    f.close()
    fealen = len(faultdata[0][0][0])-1
    V = []
    labels = []
    i = 0
    while i < len(faultdata):
        for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
            for repeattime in [1, 2, 3, 4, 5]:
                v = []
                for m in range(fealen):
                    faultfea = []
                    for expid in range(3):
                        d = faultdata[i+expid]
                        fea = d[0][d[1][0]:d[1][1]]
                        fea = [f[m+1] for f in fea]
                        faultfea += fea
                    if len(faultfea) > 50:
                        print("V4 too long")
                    normalfea1 = []
                    ndata = normaldata[bench][:math.ceil(len(faultfea)/10)]
                    for nd in ndata:
                        fea = nd[0]
                        fea = [f[m+1] for f in fea]
                        normalfea1 += fea
                    normalfea2 = []
                    ndata = normaldata[bench][len(ndata):2*len(ndata)]
                    for nd in ndata:
                        fea = nd[0]
                        fea = [f[m+1] for f in fea]
                        normalfea2 += fea
                    v.append(ks_2samp(normalfea2, faultfea)[
                             0]-ks_2samp(normalfea1, normalfea2)[0])
                    # print(ks_2samp(normalfea1,normalfea2))
                    # print(ks_2samp(normalfea2,faultfea))
                i += 3
                V.append(v)
                labels.append(faultname)
    print(faultname + ": " + str(len(V)))
    # V = np.array(V)
    # V = V.mean(axis=0)
    # print(V)
    return V, labels


# lockwait
def getV5(foldername, faultname):
    f = open(foldername + faultname + '_data.pickle', 'rb')
    faultdata = pickle.load(f)
    f.close()
    fealen = len(faultdata[0][0][0])-1
    V = []
    labels = []
    i = 0
    while i < len(faultdata):
        for bench in ['tpcc', 'tatp', 'smallbank']:
            for repeattime in [1, 2]:
                v = []
                for m in range(fealen):
                    faultfea = []
                    for expid in range(5):
                        d = faultdata[i+expid]
                        fea = d[0][d[1][0]:d[1][0]+10]
                        if d[1][0] > 100:
                            print("V5 too long")
                        fea = [f[m+1] for f in fea]
                        faultfea += fea
                    normalfea1 = []
                    ndata = normaldata[bench][:math.ceil(len(faultfea)/10)]
                    for nd in ndata:
                        fea = nd[0]
                        fea = [f[m+1] for f in fea]
                        normalfea1 += fea
                    normalfea2 = []
                    ndata = normaldata[bench][len(ndata):2*len(ndata)]
                    for nd in ndata:
                        fea = nd[0]
                        fea = [f[m+1] for f in fea]
                        normalfea2 += fea
                    v.append(ks_2samp(normalfea2, faultfea)[
                             0]-ks_2samp(normalfea1, normalfea2)[0])
                    # print(ks_2samp(normalfea1,normalfea2))
                    # print(ks_2samp(normalfea2,faultfea))
                i += 5
                V.append(v)
                labels.append(faultname)
    print(faultname + ": " + str(len(V)))
    # V = np.array(V)
    # V = V.mean(axis=0)
    # print(V)
    return V, labels


# multiindex
def getV6(foldername, faultname):
    f = open(foldername + faultname + '_data.pickle', 'rb')
    faultdata = pickle.load(f)
    f.close()
    fealen = len(faultdata[0][0][0])-1
    V = []
    labels = []
    i = 0
    while i < len(faultdata):
        for bench in ['tpcc', 'tatp', 'smallbank', 'voter']:
            for nindex in [6, 8]:
                for nclient in [5, 10]:
                    v = []
                    for m in range(fealen):
                        faultfea = []
                        for expid in range(3):
                            d = faultdata[i+expid]
                            fea = d[0]
                            fea = [f[m+1] for f in fea]
                            faultfea += fea
                        if len(faultfea) > 40:
                            print("V6 too long")
                        normalfea1 = []
                        ndata = normaldata[bench][:math.ceil(len(faultfea)/10)]
                        for nd in ndata:
                            fea = nd[0]
                            fea = [f[m+1] for f in fea]
                            normalfea1 += fea
                        normalfea2 = []
                        ndata = normaldata[bench][len(ndata):2*len(ndata)]
                        for nd in ndata:
                            fea = nd[0]
                            fea = [f[m+1] for f in fea]
                            normalfea2 += fea
                        v.append(ks_2samp(normalfea2, faultfea)[
                            0]-ks_2samp(normalfea1, normalfea2)[0])
                        # print(ks_2samp(normalfea1,normalfea2))
                        # print(ks_2samp(normalfea2,faultfea))
                    i += 3
                    V.append(v)
                    labels.append(faultname)
    print(faultname + ": " + str(len(V)))
    # V = np.array(V)
    # V = V.mean(axis=0)
    # print(V)
    return V, labels

# setknob


def getV7(foldername, faultname):
    f = open(foldername + faultname + '_data.pickle', 'rb')
    faultdata = pickle.load(f)
    f.close()
    fealen = len(faultdata[0][0][0])-1
    V = []
    labels = []
    i = 0
    while i < len(faultdata):
        for bench in ['tpcc', 'tatp', 'voter', 'smallbank']:
            v = []
            for m in range(fealen):
                faultfea = []
                fea = faultdata[i][0]
                fea = [f[m+1] for f in fea]
                faultfea = fea
                if len(faultfea) > 120:
                    print("V7 too long")
                normalfea1 = []
                ndata = normaldata[bench][:math.ceil(len(faultfea)/10)]
                for nd in ndata:
                    fea = nd[0]
                    fea = [f[m+1] for f in fea]
                    normalfea1 += fea
                normalfea2 = []
                ndata = normaldata[bench][len(ndata):2*len(ndata)]
                for nd in ndata:
                    fea = nd[0]
                    fea = [f[m+1] for f in fea]
                    normalfea2 += fea
                v.append(ks_2samp(normalfea2, faultfea)[
                         0]-ks_2samp(normalfea1, normalfea2)[0])
                # print(ks_2samp(normalfea1,normalfea2))
                # print(ks_2samp(normalfea2,faultfea))
            i += 1
            V.append(v)
            labels.append(faultname)
    print(faultname + ": " + str(len(V)))
    # V = np.array(V)
    # V = V.mean(axis=0)
    # print(V)
    return V, labels

V = []
labels = []
for foldername in foldernamelist:
    f = open(foldername + 'normal_data.pickle', 'rb')
    normaldata_ori = pickle.load(f)
    f.close()
    normaldata = {}
    # last_time = normaldata_ori[0][0][0][0]
    # last_id = 0
    # worload_ts = [last_id]
    # for id, d in enumerate(normaldata_ori):
    #     cur_time = d[0][0][0]
    #     if (cur_time-last_time).total_seconds() >= 10800 + 180:
    #         worload_ts.append(id)
    #         last_time = cur_time
    # normaldata['tpcc'] = normaldata_ori[worload_ts[0]+30:worload_ts[1]-30]
    # normaldata['tatp'] = normaldata_ori[worload_ts[1]+30:worload_ts[2]-30]
    # normaldata['voter'] = normaldata_ori[worload_ts[2]+30:worload_ts[3]-30]
    # normaldata['smallbank'] = normaldata_ori[worload_ts[3]+30:worload_ts[4]-30]

    normaldata['tpcc'] = normaldata_ori[0:180]
    normaldata['tatp'] = normaldata_ori[180:360]
    normaldata['voter'] = normaldata_ori[360:540]
    normaldata['smallbank'] = normaldata_ori[540:720]

    # faultnamelist = ['fault1','fault2','fault3','fault4','fault5','lockwait','multiindex','setknob','stress']
    faultnamelist1 = ['fault1', 'fault5']
    faultnamelist2 = ['fault2', 'fault4']
    faultnamelist3 = ['fault3']
    faultnamelist4 = ['stress']
    faultnamelist5 = ['lockwait']
    faultnamelist6 = ['multiindex']
    faultnamelist7 = ['setknob']

    for faultname in faultnamelist1:
        v, l = getV1(foldername, faultname)
        V.extend(v)
        labels.extend(l)
    for faultname in faultnamelist2:
        v, l = getV2(foldername, faultname)
        V.extend(v)
        labels.extend(l)
    for faultname in faultnamelist3:
        v, l = getV3(foldername, faultname)
        V.extend(v)
        labels.extend(l)
    for faultname in faultnamelist4:
        v, l = getV4(foldername, faultname)
        V.extend(v)
        labels.extend(l)
    for faultname in faultnamelist5:
        v, l = getV5(foldername, faultname)
        V.extend(v)
        labels.extend(l)
    for faultname in faultnamelist6:
        v, l = getV6(foldername, faultname)
        V.extend(v)
        labels.extend(l)
    for faultname in faultnamelist7:
        v, l = getV7(foldername, faultname)
        V.extend(v)
        labels.extend(l)
V = np.array(V)
labels = np.array(labels)
V = np.where(V < 0, 0, V)
print(len(V))
data = V, labels
with open('data_use_autom.pkl', 'wb') as f:
    pickle.dump(data, f)