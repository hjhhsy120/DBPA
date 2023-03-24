import pickle
import random
import numpy as np
import os
import argparse
class dataset:
    def __init__(self, test_ratio=0.2):
        self.trainfea = []
        self.trainlab = []
        self.testfea = []
        self.testlab = []
        self.allfea = []
        self.alllab = []
        self.test_ratio = test_ratio

    def gen_test_ids(self, tot):
        perm = [i for i in range(tot)]
        random.shuffle(perm)
        return set(perm[:int(tot * self.test_ratio)])

    def clear_data(self):
        self.trainfea = []
        self.trainfea = []
        self.testfea = []
        self.testlab = []
    
    def append_data(self, feature, label, is_test):
        self.allfea.append([f[1:] for f in feature])
        self.alllab.append(label)
        # if is_test:
        #     self.testfea.append([f[1:] for f in feature])
        #     self.testlab.append(label)
        # else:
        #     self.trainfea.append([f[1:] for f in feature])
        #     self.trainlab.append(label)

    def load_files1(self, file_list, time_cnt=10):
        for fname in file_list:
            try:
                f = open(fname, 'rb')
                data = pickle.load(f)
                f.close()
            except:
                print(fname, 'not found')
                continue
            test_ids = self.gen_test_ids(len(data))
            for id, d in enumerate(data):
                d_len = len(d[0])
                if d[1] == 'normal':
                    if d_len >= time_cnt:
                        self.append_data(d[0][d_len-time_cnt:], d[1], id in test_ids)
                    continue
                st = 0
                while st + time_cnt <= d_len:
                    self.append_data(d[0][st:st+time_cnt], d[1], id in test_ids)
                    st += time_cnt//2
    
    def load_files2(self, file_list, time_cnt=10):
        for fname in file_list:
            try:
                f = open(fname, 'rb')
                data = pickle.load(f)
                f.close()
            except:
                print(fname, 'not found')
                continue
            test_ids = self.gen_test_ids(len(data))
            for id, d in enumerate(data):
                d_len = len(d[0])
                st = max(d[1][0] - time_cnt // 2, 0)
                while st + time_cnt <= d_len:
                    self.append_data(d[0][st:st+time_cnt], d[2], id in test_ids)
                    st += time_cnt//2

    def load_files3(self, file_list, time_cnt=10):
        for fname in file_list:
            try:
                f = open(fname, 'rb')
                data = pickle.load(f)
                f.close()
            except:
                print(fname, 'not found')
                continue
            test_ids = self.gen_test_ids(len(data))
            for id, d in enumerate(data):
                if d[1][0] >= time_cnt:
                    self.append_data(d[0][d[1][0]-time_cnt : d[1][0]], 'normal', id in test_ids)
                st = max(d[1][0] - time_cnt // 2, 0)
                while st + time_cnt <= d[1][1]:
                    self.append_data(d[0][st:st+time_cnt], d[2], id in test_ids)
                    st += time_cnt//2
    def load_files4(self, file_list, time_cnt=10):
        for fname in file_list:
            try:
                f = open(fname, 'rb')
                data = pickle.load(f)
                f.close()
            except:
                print(fname, 'not found')
                continue
            test_ids = self.gen_test_ids(len(data))
            for id, d in enumerate(data):
                self.append_data(d[0][0:time_cnt], 'normal', id in test_ids)
    def output_result(self, file_name):
        f = open(file_name, 'wb')
        pickle.dump((self.trainfea, self.trainlab, self.testfea, self.testlab), f)
        f.close()
        return len(self.trainlab), len(self.testlab), set(self.trainlab + self.testlab)

    def split_data(self):
        labels = set(self.alllab)
        for label in labels:
            fea = []
            lab = []
            for i in range(len(self.allfea)):
                if self.alllab[i] == label:
                    fea.append(self.allfea[i])
                    lab.append(self.alllab[i])
            test_ids = self.gen_test_ids(len(fea))
            for i in range(len(fea)):
                self.append_splited_data(fea[i], lab[i], i in test_ids)

    def append_splited_data(self, feature, label, is_test):
        if is_test:
            self.testfea.append(feature)
            self.testlab.append(label)
        else:
            self.trainfea.append(feature)
            self.trainlab.append(label)
    
    def print_cnt(self):
        print("All")
        labels = set(self.alllab)
        labels_cnt_all = {}
        for label in labels:
            labels_cnt_all[label] = 0.0
        for i in range(len(self.alllab)):
            labels_cnt_all[self.alllab[i]] += 1
        print(labels_cnt_all)
        print("train")
        labels = set(self.trainlab)
        labels_cnt = {}
        for label in labels:
            labels_cnt[label] = 0.0
        for i in range(len(self.trainlab)):
            labels_cnt[self.trainlab[i]] += 1
        print(labels_cnt)
        train_ratio = [labels_cnt[k]/labels_cnt_all[k] for k in labels_cnt_all]
        print(train_ratio)
        if self.test_ratio == 0:
            return
        print("test")
        labels = set(self.testlab)
        labels_cnt = {}
        for label in labels:
            labels_cnt[label] = 0.0
        for i in range(len(self.testlab)):
            labels_cnt[self.testlab[i]] += 1
        print(labels_cnt)
        test_ratio = [labels_cnt[k]/labels_cnt_all[k] for k in labels_cnt_all]
        print(test_ratio)

def gen_paths(folder_list, file_list):
    result = []
    for folder in folder_list:
        result += [folder + '/' + f + '_data.pickle' for f in file_list]
    return result

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Arguments from CMD')
    parser.add_argument('--test_ratio', type=float, default=0.0, help='test_ratio')
    parser.add_argument('--folder_list', type=str, default='', help='folder_list')
    parser.add_argument('--result_name', type=str, default='data_use', help='result_name')
    args = parser.parse_args()
    a = dataset(args.test_ratio)
    folder_list = list(args.folder_list.split(','))
    result_name = args.result_name
    list1 = ['setknob', 'multiindex']
    list2 = ['lockwait']
    list3 = ['fault1', 'fault2', 'fault3', 'fault4', 'fault5', 'stress']
    list4 = ['normal']
    # folder_list = ['32_128/single/','32_256/single/','64_128/single/','64_256/single/']
    a.load_files1(gen_paths(folder_list, list1))
    a.load_files2(gen_paths(folder_list, list2))
    a.load_files3(gen_paths(folder_list, list3))
    a.load_files4(gen_paths(folder_list, list4))
    a.split_data()
    a.print_cnt()
    traincnt, testcnt, labels = a.output_result(result_name + '.pkl')

    print('training:', traincnt)
    print('test:', testcnt)
    print('labels:')
    for l in labels:
        print(l)
    