from utils import *
from collections import Counter
import argparse
# print P, R and F1 of every fault
print_per_fault = False
# set the number of fault data equal to the number of normal data
set_fault_num = True

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Arguments from CMD')
    parser.add_argument('--data_file', type=str, default='', help='data_file')
    parser.add_argument('--model_name_list', type=str, default='OneClassSVM', help='model_name_list')
    parser.add_argument('--print_per_fault', type=int, default=0, help='print_per_fault')
    parser.add_argument('--set_fault_num', type=int, default=1, help='set_fault_num')
    args = parser.parse_args()
    data_file = args.data_file
    model_name_list = list(args.model_name_list.split(','))
    # print P, R and F1 of every fault
    print_per_fault = args.print_per_fault == 1
    # set the number of fault data equal to the number of normal data
    set_fault_num = args.set_fault_num == 1
    # model_name_list = ['IsolationForest', 'OneClassSVM',
    #                    'LocalOutlierFactor', 'SVDD']
    data = load_data(data_file + '.pkl')
    all_results = []
    best_model_ids = []
    print('Start training')
    trainfea, trainlab, testfea, testlab = data
    # relabel the data
    trainlab = [1 if x == 'normal' else -1 for x in trainlab]
    newtrainfea = []
    for i in range(len(trainfea)):
        if trainlab[i] == 1:
            newtrainfea.append(trainfea[i])
    trainfea = newtrainfea
    trainfea = np.array(trainfea)
    print(len(newtrainfea))

    if set_fault_num:
        faultcnt = Counter(testlab)
        ratio = faultcnt['normal'] / (len(testlab) - faultcnt['normal'])
        del faultcnt['normal']
        for key in faultcnt.keys():
            faultcnt[key] = round(faultcnt[key]*ratio)
        newtestfea = []
        newtestlab = []
        testlabname = []
        for i in range(len(testfea)):
            if testlab[i] == 'normal':
                newtestfea.append(testfea[i])
                newtestlab.append(1)
                testlabname.append(testlab[i])
            elif faultcnt[testlab[i]] > 0:
                newtestfea.append(testfea[i])
                newtestlab.append(-1)
                faultcnt[testlab[i]] -= 1
                testlabname.append(testlab[i])
        testfea = newtestfea
        testfea = np.array(testfea)
        testlab = newtestlab
        print(len(newtestfea))
    else:
        testlabname = testlab.copy()
        testlab = [1 if x == 'normal' else -1 for x in testlab]

    for model_name in model_name_list:
        model = get_model(model_name)
        model.train(trainfea)
        testpred = model.predict(testfea)
        tp, fp, tn, fn = 0, 0, 0, 0

        if print_per_fault:
            faulttp = {'1': 0, '2': 0,  '3': 0, '4': 0, '5': 0, 'IO': 0,
                       'manyindex': 0, 'lockwait': 0, 'knob_shared_buffers': 0}
            faultfn = {'1': 0, '2': 0,  '3': 0, '4': 0, '5': 0, 'IO': 0,
                       'manyindex': 0, 'lockwait': 0, 'knob_shared_buffers': 0}

        for i in range(len(testlab)):
            if testlab[i] == -1:
                if testpred[i] == -1:
                    if print_per_fault:
                        faulttp[testlabname[i]] += 1
                    tp += 1
                else:
                    if print_per_fault:
                        faultfn[testlabname[i]] += 1
                    fn += 1
            else:
                if testpred[i] == -1:
                    fp += 1
                else:
                    tn += 1
        p = tp / (tp + fp)
        r = tp / (tp + fn)
        f1 = 2 * p * r / (p + r)
        # P, R and F1 of each model
        print('{:<20}\tP = {:.4f}\tR = {:.4f}\tF1 = {:.4f}'.format(
            model_name, p, r, f1))

        if print_per_fault:
            # P, R and F1 of each fault
            for faultname in faulttp.keys():
                p = faulttp[faultname] / (faulttp[faultname] + fp)
                r = faulttp[faultname] / \
                    (faulttp[faultname] + faultfn[faultname])
                if p+r == 0:
                    f1 = 0
                else:
                    f1 = 2 * p * r / (p + r)
                print('{:<20}\tP = {:.4f}\tR = {:.4f}\tF1 = {:.4f}'.format(
                    faultname, p, r, f1))

            print()
