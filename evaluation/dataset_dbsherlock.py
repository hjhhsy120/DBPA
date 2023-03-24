import pickle
import argparse
parser = argparse.ArgumentParser(description='Arguments from CMD')
parser.add_argument('--data_cnt', type=int, default=40, help='data_cnt')
args = parser.parse_args()
data_cnt = args.data_cnt

datafolder = 'faultdata_'+str(data_cnt)+'/'
trainfea = []
trainlab = []
testfea = []
testlab = []
def append_data(feature, label,is_test):
    if is_test:
        testfea.append([f[1:] for f in feature])
        testlab.append(label)
    else:
        trainfea.append([f[1:] for f in feature])
        trainlab.append(label)

for filename in ['fault1_data', 'fault2_data', 'fault3_data', 'fault4_data', 'fault5_data', 'multiindex_data', 'setknob_data', 'stress_data', 'lockwait_data']:
    f = open('dbsherlock_data/' + datafolder + filename + '.pickle', 'rb')
    traindata, testdata = pickle.load(f)
    f.close()
    for d in traindata:
        if isinstance(d[1], str):
            append_data(d[0][12:22],d[1],False)
            append_data(d[0][1:11],'normal',False)
        else:
            append_data(d[0][d[1][0]+1:d[1][0]+11],d[2],False)
            if d[2] == 'manyindex':
                append_data(d[0][1:11],'normal',False)
    for d in testdata:
        if isinstance(d[1], str):
            append_data(d[0][12:22],d[1],True)
            append_data(d[0][1:11],'normal',True)
        else:
            append_data(d[0][d[1][0]+1:d[1][0]+11],d[2],True)
            if d[2] == 'manyindex':
                append_data(d[0][1:11],'normal',True)

for i in range(len(trainfea)):
    if len(trainfea[i]) != 10:
        print('error in train num: ' + str(i))
for i in range(len(testfea)):
    if len(testfea[i]) != 10:
        print('error in test num: ' + str(i))


print("train")
labels = set(trainlab)
labels_cnt = {}
for label in labels:
    labels_cnt[label] = 0.0
for i in range(len(trainlab)):
    labels_cnt[trainlab[i]] += 1
print(labels_cnt)
print("test")
labels = set(testlab)
labels_cnt = {}
for label in labels:
    labels_cnt[label] = 0.0
for i in range(len(testlab)):
    labels_cnt[testlab[i]] += 1
print(labels_cnt)



f = open('data_use_dbsherlock_'+str(data_cnt)+'.pkl', 'wb')
pickle.dump((trainfea, trainlab, testfea, testlab), f)
f.close()
    
    