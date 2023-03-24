
from gc import garbage
import pickle
from typing import Counter
import numpy as np
import collections
import time
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support
from models import *
all_labels = []
# from sklearn.metrics import precision_score
# from sklearn.metrics import recall_score
import warnings
warnings.filterwarnings('ignore')

# load all data from the file


def load_data(file_name):
    with open(file_name, 'rb') as f:
        data = pickle.load(f)
    trainfea, trainlab, testfea, testlab = data
    for i in range(len(trainfea)):
        trainfea[i] = np.array(trainfea[i]).flatten()
    for i in range(len(testfea)):
        testfea[i] = np.array(testfea[i]).flatten()
    trainfea = np.array(trainfea).reshape(len(trainfea), -1)
    testfea = np.array(testfea).reshape(len(testfea), -1)
    return trainfea, trainlab, testfea, testlab

# only load train data from the file


def load_train_data(file_name):
    with open(file_name, 'rb') as f:
        data = pickle.load(f)
    trainfea, trainlab, _, _ = data
    for i in range(len(trainfea)):
        trainfea[i] = np.array(trainfea[i]).flatten()
    trainfea = np.array(trainfea).reshape(len(trainfea), -1)
    return trainfea, trainlab

# load dictionary of fault name


def load_labels(file_name='data/labels.txt'):
    f = open(file_name, 'r')
    d = {}
    for l in f.readlines():
        if ':' in l:
            ls = l.strip().split(':')
            d[ls[0]] = ls[1]
    return d

# load metrics' name


def load_head(file_name='data/head.txt'):
    f = open(file_name, 'r')
    head = f.readline().strip().split(',')
    f.close()
    return head

# relabel data (set current fault to 1, set normal data and other faults to 0)


def relabel_data(data, label):
    trainfea, trainlab0, testfea, testlab0 = data
    trainlab = [1 if x == label else 0 for x in trainlab0]
    testlab = [1 if x == label else 0 for x in testlab0]
    return trainfea, trainlab, testfea, testlab

# calculate P, R and F1


def pr_values(result):
    tp, fp, tn, fn = result
    if tp == 0:
        return 0.0, 0.0, 0.0
    else:
        p = tp / (tp + fp)
        r = tp / (tp + fn)
        f1 = 2 * p * r / (p + r)
        return p, r, f1

# evaluate results


def eval_results(pred, truth):
    tp, fp, tn, fn = 0, 0, 0, 0
    for i in range(len(truth)):
        if truth[i] == 1:
            if pred[i] == 1:
                tp += 1
            else:
                fn += 1
        else:
            if pred[i] == 1:
                fp += 1
            else:
                tn += 1
    _, _, f1 = pr_values([tp, fp, tn, fn])
    return tp, fp, tn, fn, f1

# evaluate the model


def eval(model, testfea, testlab):
    result = model.predict(testfea)
    testpred = [round(x) for x in result]
    return eval_results(testpred, testlab)

# get the important features of the model


def get_important_features(model, head, method='model', trainfea=None):
    fea_len = len(head)
    if method == 'shap':
        feature_importance = model.get_shap_importance(trainfea)
    else:
        feature_importance = model.get_feature_importance()
    fea_cnt = {}
    for h in head:
        fea_cnt[h] = 0.0
    for j in range(len(feature_importance)):
        fea_cnt[head[j % fea_len]] += feature_importance[j]
    fea_cnt = collections.Counter(fea_cnt).most_common()
    ranking = [fea_cnt[i][0] for i in range(len(fea_cnt))]

    filters = ['sockets', 'procs', 'conn', 'virtual_memory_minpf']
    result = []
    for fea in ranking:
        flag = True
        for fil in filters:
            if fil in fea:
                flag = False
                break
        if flag:
            result.append(fea)
    return result


def get_model(model_name):
    # ['Linear', 'DecisionTree', 'RandomForest', 'XGBoost', 'LightGBM']
    # [lr_model(), dt_model(), rf_model(), xgb_model(), lgb_model()]

    # # load model from file
    # with open('results/seps/multiclass_' + model_name + '.pkl', 'rb') as f:
    #     model = pickle.load(f)
    # return model

    if model_name == 'Linear':
        return lr_model()
    elif model_name == 'DecisionTree':
        return dt_model()
    elif model_name == 'RandomForest':
        return rf_model()
    elif model_name == 'XGBoost':
        return xgb_model()
    elif model_name == 'LightGBM':
        return lgb_model()
    elif model_name == 'MLP':
        return mlp_model()
    elif model_name == 'IsolationForest':
        return if_model()
    elif model_name == 'OneClassSVM':
        return ocs_model()
    elif model_name == 'DBSCAN':
        return dbs_model()
    elif model_name == 'LocalOutlierFactor':
        return lof_model()
    elif model_name == 'EllipticEnvelope':
        return ee_model()
    elif model_name == 'SVDD':
        return svdd_model()
    else:
        return blank_model()


def important_features(model, trainfea, trainlab, head, feature_path):
    IMPORTANT_FEA_NUM_MODEL = 5
    IMPORTANT_FEA_NUM = 10

    ranking1 = get_important_features(model, head)
    surrogate = rf_model()
    trainfea2 = normalize(trainfea)
    surrogate.train(trainfea2, trainlab)
    ranking2 = get_important_features(model, head, 'shap', trainfea2)
    topk = ranking1[:IMPORTANT_FEA_NUM_MODEL]
    for fea in ranking2:
        if not fea in topk:
            topk.append(fea)
            if len(topk) >= IMPORTANT_FEA_NUM:
                break

    f = open(feature_path, 'w')
    for i in range(IMPORTANT_FEA_NUM):
        f.writelines([topk[i]])
        if i < IMPORTANT_FEA_NUM-1:
            f.writelines(",")
    f.close()

    return topk

# train model (2-classifier)


def train(model_name_list, data, model_path):
    # initialize
    trainfea, trainlab, testfea, testlab = data
    # print('train: {}'.format(len(trainfea)))
    # print('test: {}'.format(len(testfea)))
    model_list = [get_model(model_name) for model_name in model_name_list]
    best_f1 = 0.0
    best_model_id = 0
    results = []

    # train and evaluate
    for model_id, model in enumerate(model_list):
        model.train(trainfea, trainlab)
        tp, fp, tn, fn, f1 = eval(model, trainfea, trainlab)
        # tp, fp, tn, fn, f1 = eval(model, testfea, testlab)
        if f1 >= best_f1:
            best_f1 = f1
            best_model_id = model_id
        results.append([tp, fp, tn, fn])

    # save model
    with open(model_path, 'wb') as f:
        pickle.dump(model_list[best_model_id], f)
    return best_model_id, model_list, results

# train model (multi-classifier)


def train_multiclass(model_name_list, data, model_path, save_model):
    # initialize
    trainfea, trainlab, testfea, testlab = data
    # print('train: {}'.format(len(trainfea)))
    # print('test: {}'.format(len(testfea)))
    model_list = [get_model(model_name) for model_name in model_name_list]
    best_acc = 0.0
    best_model_id = 0
    results = []
    labels = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    # train and evaluate
    for model_id, model in enumerate(model_list):
        train_start = time.time()
        model.train(trainfea, trainlab)
        train_end = time.time()
        train_time = train_end-train_start
        result = model.predict(testfea)
        lockwait_res = []
        # for i in range(len(testlab)):
        #     if testlab[i] == 5:
        #         lockwait_res.append(all_labels[result[i]])
        # g = Counter(lockwait_res)
        # print(g)
        acc = accuracy_score(testlab, result)
        prf = precision_recall_fscore_support(testlab, result, labels=labels)
        if acc >= best_acc:
            best_acc = acc
            best_model_id = model_id
        results.append([acc, prf, train_time])
        print("{} done".format(model_name_list[model_id]))

    # save model
    if save_model:
        for model_id, model_name in enumerate(model_name_list):
            with open(model_path + model_name + '.pkl', 'wb') as f:
                pickle.dump(model_list[model_id], f)
    return best_model_id, model_list, results


# relabel data for multi-classifier (from string to integer)
def relabel_data_multiclass(data, labels):
    trainfea, trainlab0, testfea, testlab0 = data
    trainlab = []
    testlab = []
    global all_labels
    all_labels.extend(labels)
    all_labels.append('normal')
    print(labels)
    for x in trainlab0:
        if x not in labels:
            trainlab.append(len(labels))
        else:
            trainlab.append(labels.index(x))
    for x in testlab0:
        if x not in labels:
            testlab.append(len(labels))
        else:
            testlab.append(labels.index(x))
    return trainfea, trainlab, testfea, testlab
