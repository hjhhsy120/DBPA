from sklearn.preprocessing import StandardScaler
import numpy as np
import pickle
import argparse

def normalize(trainfea, testfea):
    transfer = StandardScaler()
    train_cnt = len(trainfea)
    metrics_cnt = len(trainfea[0][0])
    all_fea = np.array(trainfea + testfea)
    all_fea = all_fea.reshape([-1, metrics_cnt])
    normed=transfer.fit_transform(all_fea)
    result = list(normed.reshape([-1, 10, metrics_cnt]))
    return result[:train_cnt], result[train_cnt:]

parser = argparse.ArgumentParser(description='Arguments from CMD')
parser.add_argument('--data_name', type=str, default='data_use', help='data_name')
args = parser.parse_args()
data_name = args.data_name
with open(data_name + '.pkl', 'rb') as f:
    data = pickle.load(f)
train_fea, train_lab, test_fea, test_lab = data
train_fea,test_fea = normalize(train_fea,test_fea)
print('train cnt:{}'.format(len(train_fea)))
print('test cnt:{}'.format(len(test_fea)))
print('all cnt:{}'.format(len(train_fea)+len(test_fea)))
print('train ratio:{}'.format(len(train_fea)/1.0/(len(train_fea)+len(test_fea))))
data = train_fea,train_lab,test_fea,test_lab
with open(data_name + '_norm.pkl', 'wb') as f:
    pickle.dump(data,f)