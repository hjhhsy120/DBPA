import lightgbm as lgb
import sklearn.linear_model as lm
import sklearn.preprocessing as sp
import sklearn.pipeline as pl
import sklearn.tree as tr
import sklearn.ensemble as es
import sklearn.neural_network as nn
from xgboost import XGBClassifier
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN
from sklearn.neighbors import LocalOutlierFactor
from sklearn.covariance import EllipticEnvelope
import random
import shap
import numpy as np


def normalize(data):
    mean_val = np.mean(data, axis=0)
    std_val = np.std(data, axis=0)
    for i in range(len(std_val)):
        if std_val[i] == 0:
            std_val[i] = 1
    result = []
    for d in data:
        result.append((np.array(d) - mean_val) / std_val)
    return np.array(result)

class lr_model:
    def __init__(self):
        self.model = lm.LogisticRegression(max_iter=1000)

    def train(self, trainfea, trainlab):
        self.std_val = np.std(trainfea, axis=0)
        self.model.fit(trainfea, trainlab)
        self.fea_len = len(trainfea[0])

    def predict(self, testfea):
        return self.model.predict(testfea)
    
    def get_feature_importance(self):
        return [abs(x) / self.std_val[id] for id, x in enumerate(self.model.coef_[0])]
    
    def get_shap_importance(self, trainfea):
        trainfea2 = normalize(trainfea)
        explainer = shap.LinearExplainer(self.model, trainfea2)
        shap_values = explainer(trainfea2)
        return np.mean(np.abs(shap_values[:,:].values), axis=0)

class polynomial_model:
    def __init__(self):
        self.model = pl.make_pipeline(
            sp.PolynomialFeatures(1),  
            sp.StandardScaler(),
            lm.LogisticRegression(max_iter=2000)  
        )

    def train(self, trainfea, trainlab):
        self.model.fit(trainfea, trainlab)
        self.fea_len = len(trainfea[0])

    def predict(self, testfea):
        return self.model.predict(testfea)

    def get_feature_importance(self):
        # TODO
        return [random.random() for _ in range(self.fea_len)]
    
    def get_shap_importance(self, trainfea):
        # NOT FEASABLE
        return [random.random() for _ in range(self.fea_len)]
        # X100 = shap.utils.sample(trainfea, 100)
        # explainer = shap.PermutationExplainer(self.model.named_steps['logisticregression'].predict, self.model[:-1].transform(X100))
        # shap_values = explainer.shap_values(self.model[:-1].transform(X100))
        # return np.average(np.abs(shap_values[:,:].values), axis=1)

class dt_model:
    def __init__(self):
        self.model = tr.DecisionTreeClassifier(criterion='gini', max_depth=15,random_state=42)

    def train(self, trainfea, trainlab):
        self.model.fit(trainfea, trainlab)

    def predict(self, testfea):
        return self.model.predict(testfea)

    def get_feature_importance(self):
        return list(self.model.feature_importances_)

    def get_shap_importance(self, trainfea):
        explainer = shap.Explainer(self.model)
        shap_values = explainer(trainfea)
        vals = shap_values[:,:].values
        return np.mean(np.abs(vals[:,:,1]), axis=0)

class rf_model:
    def __init__(self):
        self.model = es.RandomForestClassifier(
            criterion='gini', max_depth=30, random_state=42)

    def train(self, trainfea, trainlab):
        self.model.fit(trainfea, trainlab)

    def predict(self, testfea):
        return self.model.predict(testfea)

    def get_feature_importance(self):
        return list(self.model.feature_importances_)

    def get_shap_importance(self, trainfea):
        explainer = shap.Explainer(self.model)
        shap_values = explainer(trainfea)
        vals = shap_values[:,:].values
        return np.mean(np.abs(vals[:,:,1]), axis=0)

class xgb_model:
    def __init__(self):
        self.model = XGBClassifier(eval_metric='error', use_label_encoder=False,random_state=42)

    def train(self, trainfea, trainlab):
        self.model.fit(trainfea, trainlab)

    def predict(self, testfea):
        return self.model.predict(testfea)

    def get_feature_importance(self):
        return list(self.model.feature_importances_)

    def get_shap_importance(self, trainfea):
        explainer = shap.Explainer(self.model)
        shap_values = explainer(trainfea)
        return np.mean(np.abs(shap_values[:,:].values), axis=0)

class lgb_model:
    def __init__(self):
        self.model = lgb.LGBMClassifier(random_state=42)

    def train(self, trainfea, trainlab):
        self.model.fit(trainfea, trainlab)

    def predict(self, testfea):
        return self.model.predict(testfea)

    def get_feature_importance(self):
        return list(self.model.feature_importances_)

    def get_shap_importance(self, trainfea):
        explainer = shap.Explainer(self.model)
        shap_values = explainer(trainfea)
        vals = shap_values[:,:].values
        return np.mean(np.abs(vals[:,:,1]), axis=0)

class mlp_model:
    def __init__(self):
        self.model = nn.MLPClassifier()

    def train(self, trainfea, trainlab):
        self.model.fit(trainfea, trainlab)
        self.fea_len = len(trainfea[0])

    def predict(self, testfea):
        return self.model.predict(testfea)
    
    def get_feature_importance(self):
        # TODO
        return [random.random() for _ in range(self.fea_len)]
    
    def get_shap_importance(self, trainfea):
        # NOT FEASABLE
        return [random.random() for _ in range(self.fea_len)]

class if_model:
    def __init__(self):
        self.model = IsolationForest(random_state=42)

    def train(self, trainfea):
        self.model.fit(trainfea)

    def predict(self, testfea):
        result = self.model.predict(testfea)
        return [round(x) for x in result]

class ocs_model:
    def __init__(self):
        self.model = OneClassSVM(kernel='linear')

    def train(self, trainfea):
        self.model.fit(trainfea)

    def predict(self, testfea):
        result = self.model.predict(testfea)
        return [round(x) for x in result]
    
class dbs_model:
    def __init__(self):
        self.model = DBSCAN()

    def train(self, trainfea):
        self.model.fit(trainfea)

    def predict(self, testfea):
        result = self.model.predict(testfea)
        return [round(x) for x in result]

class lof_model:
    def __init__(self):
        self.model = LocalOutlierFactor(novelty=True)

    def train(self, trainfea):
        self.model.fit(trainfea)

    def predict(self, testfea):
        result = self.model.predict(testfea)
        return [round(x) for x in result]

class ee_model:
    def __init__(self):
        self.model = EllipticEnvelope()

    def train(self, trainfea):
        self.model.fit(trainfea)

    def predict(self, testfea):
        result = self.model.predict(testfea)
        return [round(x) for x in result]

class svdd_model:
    def __init__(self):
        self.model = OneClassSVM()

    def train(self, trainfea):
        self.model.fit(trainfea)

    def predict(self, testfea):
        result = self.model.predict(testfea)
        return [round(x) for x in result]
    # def __init__(self):
    #     self.model = BaseSVDD(C=0.9, gamma=0.3, kernel='rbf', display='off')

    # def train(self, trainfea):
    #     self.model.fit(trainfea)

    # def predict(self, testfea):
    #     result = self.model.predict(testfea)
    #     return [round(x.max()) for x in result]
    
    
class blank_model:
    def __init__(self):
        pass

    def train(self, trainfea, trainlab):
        self.fea_len = len(trainfea[0])

    def predict(self, testfea):
        return [random.randint(0, 1) for _ in range(len(testfea))]
    
    def get_feature_importance(self):
        return [random.random() for _ in range(self.fea_len)]

    def get_shap_importance(self, trainfea):
        return [random.random() for _ in range(self.fea_len)]


