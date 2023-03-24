import pickle
import numpy as np

model_name_list = ['Random Forest', 'LightGBM']

f = open('features/all.txt','r')
l = f.readline().strip()
f.close()
heads = l.split(',')

f = open('features/important.txt','r')
l = f.readline().strip()
f.close()
important = l.split(',')

id_list = []
models = {}
for model_name in model_name_list:
    models[model_name] = []
for iii in important:
    idx = heads.index(iii)
    id_list.append(idx)
    for model_name in model_name_list:
        f = open('models/' + model_name + '_' + str(idx) + '.pkl', 'rb')
        model = pickle.load(f)
        f.close()
        models[model_name].append(model)

mm, ss = pickle.load(open('features/mean_std.pkl', 'rb'))

def myavg(s1, s2):
    return np.divide(s1+s2, 2)

def ml(s1, s2, normal, xx):
    models_use = xx
    result = myavg(s1, s2)
    feas = []
    for i in range(10):
        fea = list(s1[i]) + list(s2[i]) + list(normal[i])
        feas.append(fea)
    feas = np.array(feas)
    for i, idx in enumerate(id_list):
        pred = models_use[i].predict(feas)
        for j in range(10):
            result[j][idx] = pred[j]
    return result

def gen_data(data, same_type=False):
    preds = []
    for s1, s2, normal in data:
        s1 = np.array(s1)
        s2 = np.array(s2)
        normal = np.array(normal)
        if same_type:
            pred = ml(s1, s2, normal, models['Random Forest'])
        else:
            pred = ml(s1, s2, normal, models['LightGBM'])
        pred1 = []
        for p in pred:
            p1 = np.array(p) * ss + mm
            pred1.append(p1)
        preds.append(np.array(pred1))
    
    return preds

