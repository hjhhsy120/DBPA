from utils import *
from sklearn.model_selection import train_test_split
import argparse
workloads = ['data_use_tpcc_norm','data_use_tatp_norm','data_use_voter_norm','data_use_smallbank_norm']
systems = ['data_use_32_128_norm','data_use_32_256_norm','data_use_64_128_norm','data_use_64_256_norm']
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Arguments from CMD')
    parser.add_argument('--train_file', type=str, default='', help='train_file')
    parser.add_argument('--test_file', type=str, default='', help='test_file')
    parser.add_argument('--labels_file', type=str, default='labels.txt', help='labels_file')
    parser.add_argument('--head_file', type=str, default='head.txt', help='head_file')
    parser.add_argument('--is_diversity', type=int, default=0, help='is_diversity')
    parser.add_argument('--model_name_list', type=str, default='XGBoost', help='model_name_list')
    parser.add_argument('--save_model', type=int, default=0, help='save_model')
    parser.add_argument('--model_path', type=str, default='', help='model_path')
    args = parser.parse_args()
    train_file = args.train_file
    test_file = args.test_file
    labels_file = args.labels_file
    head_file = args.head_file
    is_diversity = args.is_diversity
    model_name_list = list(args.model_name_list.split(','))
    save_model = args.save_model
    model_path = args.model_path
    fault_cnt = 9
    if test_file in workloads:
        fault_cnt -= 1
    # load data
    if is_diversity == 1:
        # load data in different environments (for diversity test)
        if train_file==test_file:
            fea,lab= load_train_data(train_file + '.pkl')
            train_fea, test_fea, train_lab, test_lab = train_test_split(
            fea, lab, stratify=lab, test_size=0.4, random_state=42)  
        else:
            if train_file == 'others':
                train_fea = []
                train_lab = []
                if test_file in workloads:
                    for file in workloads:
                        if file != test_file:
                            train_fea0,train_lab0 = load_train_data(file + '.pkl')
                            if len(train_fea) == 0:
                                train_fea = train_fea0
                                train_lab = train_lab0
                            else:
                                train_fea = np.concatenate([train_fea,train_fea0])
                                train_lab = np.concatenate([train_lab,train_lab0])
                else:
                    for file in systems:
                        if file != test_file:
                            train_fea0,train_lab0 = load_train_data(file + '.pkl')
                            if len(train_fea) == 0:
                                train_fea = train_fea0
                                train_lab = train_lab0
                            else:
                                train_fea = np.concatenate([train_fea,train_fea0])
                                train_lab = np.concatenate([train_lab,train_lab0])
            else:
                train_fea,train_lab= load_train_data(train_file + '.pkl')
            test_fea,test_lab = load_train_data(test_file + '.pkl')
        data = train_fea,train_lab,test_fea,test_lab
        print('train cnt: ' + str(len(train_fea)))
        print('test cnt: ' + str(len(test_fea)))

    else:
        data = load_data(train_file + '.pkl')
        print('train cnt: ' + str(len(data[0])))
        print('test cnt: ' + str(len(data[2])))

    labels = load_labels(labels_file)
    head = load_head(head_file)
    # model_name_list = ['Linear','MLP', 'DecisionTree',
    #                    'RandomForest', 'XGBoost', 'LightGBM']
    # model_name_list = ['DecisionTree','RandomForest']
    # model_name_list = ['XGBoost']
    all_results = []
    best_model_ids = []

    print('Start training')
    data_use = relabel_data_multiclass(data, list(labels.keys()))
    best_model_id, model_list, results = train_multiclass(
        model_name_list, data_use, model_path, save_model==1)
    best_model_ids.append(best_model_id)
    all_results.append(results)
    # topk = important_features(model_list[best_model_id], data_use[0], data_use[1], head,
    #                           'results/important_features/multiclass.txt')

    # Accuracy of each model
    labels = list(labels.keys())
    for model_id in range(len(model_name_list)):
        print('{:<15}\tTrain time = {:.4f}\tAcc = {:.4f}'.format(
            model_name_list[model_id], results[model_id][2], results[model_id][0]))

        # P, R and F1 of each fault
        for j in range(fault_cnt):
            print('{:<25}\t{:.4f},{:.4f},{:.4f}'.format(
                labels[j], results[model_id][1][0][j], results[model_id][1][1][j], results[model_id][1][2][j]))
        print()

    # print('Top{} features:'.format(len(topk)), end='')
    # for fea in topk:
    #     print('\t' + fea, end='')
    print()

    # Accuracy of best model
    print('best model: {}\tTrain time = {:.4f}\tAcc = {:.4f}'.format(
        model_name_list[best_model_id], results[model_id][2], results[best_model_id][0]))
