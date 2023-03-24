import numpy as np
import random
from filter_with_domain_knowledge import filter_with_domain_knowledge
import json
import pickle
import time
import datetime
import argparse


class ExperimentParameter:
    def __init__(self):
        self.delay = 0
        self.num_discrete = 50
        self.diff_threshold = 0.2
        self.abnormal_multiplier = 10
        self.create_model = True
        self.cause_string = 'stress_data'
        self.model_name = 'stress_data1'
        self.find_lag = False
        self.introduce_lag = True
        self.lag_min = 0
        self.lag_max = 0
        self.expand_normal_region = False
        self.expand_normal_size = 1000
        self.domain_knowledge = []
        self.correct_filter_list = []


parser = argparse.ArgumentParser(description='Arguments from CMD')
parser.add_argument('--data_cnt', type=int, default=40, help='data_cnt')
parser.add_argument('--head_file', type=str,default='head.txt', help='head_file')
args = parser.parse_args()
head_file = args.head_file
data_cnt = args.data_cnt

datafolder = './dbsherlock_data/faultdata_'+str(data_cnt)+'/'
model_directory = './dbsherlock_model/causal_model_'+str(data_cnt)
time_total = 0
time_start_all = time.time()
print('train start: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

for filename in ['fault1_data', 'fault2_data', 'fault3_data', 'fault4_data', 'fault5_data', 'multiindex_data', 'setknob_data', 'stress_data', 'lockwait_data']:
    f = open(datafolder+filename+'.pickle', 'rb')
    traindata, _ = pickle.load(f)
    print(len(traindata))
    f.close()
    time_start = time.time()
    for num in range(len(traindata)):
        one_test_datasets = traindata[num][0]

        if isinstance(traindata[num][1], str):
            # print("label111", traindata[num][1])
            one_abnormal_regions = np.arange(12, len(one_test_datasets), 1)
        elif isinstance(traindata[num][1], list) and len(traindata[num][1]) == 1:
            # print("label222", traindata[num][2])
            one_abnormal_regions = np.arange(
                traindata[num][1][0], traindata[num][1][0] + 12, 1)
        else:
            # print("label333", traindata[num][2])
            one_abnormal_regions = np.arange(
                traindata[num][1][0], traindata[num][1][1] + 1, 1)

        exp_param = ExperimentParameter()
        exp_param.cause_string = filename
        exp_param.model_name = filename+str(num)

        one_normal_regions = []
        attribute_types = []

        data = one_test_datasets
        for i in range(len(data)):
            data[i][0] = 1

        with open(head_file, 'r+', encoding='utf-8') as f:
            s = [i[:-1].split(',') for i in f.readlines()]
        filed_names = s[0]
        filed_names.insert(0, "time")
        extra = {}
        has_predicate = 0
        in_conflict = 1
        normal_partition = 1
        abnormal_partition = 2
        numeric = 0
        categorical = 1

        numRow = len(data)
        numAttr = len(data[0])
        # print("numRow",numRow,"numAttr",numAttr)
        if len(attribute_types) == 0:
            attribute_types = np.zeros((1, numAttr))[0]
            attribute_types = attribute_types.tolist()
        # print("len(attribute_types)",len(attribute_types))
        # dbsherlock parameters
        num_discrete = exp_param.num_discrete
        normalized_diff_threshold = exp_param.diff_threshold
        abnormal_multiplier = exp_param.abnormal_multiplier
        createModel = exp_param.create_model
        causeStr = exp_param.cause_string
        modelName = exp_param.model_name

        lags = np.zeros((1, numAttr))[0]
        detected_lag_error = []
        lagged_abnormal_indexes = []
        lagged_normal_indexes = []

        # introduce a random lag for each attribute.
        if exp_param.introduce_lag:
            lagged_abnormal_indexes.append([])
            for i in range(1, numAttr):
                lagged_abnormalIdx = []
                random_lag = random.randint(
                    exp_param.lag_min, exp_param.lag_max)
                lags[i] = random_lag
                for temp in one_abnormal_regions:
                    lagged_abnormalIdx.append(temp + random_lag)

                if max(lagged_abnormalIdx) > numRow:
                    min_ind = min(lagged_abnormalIdx)
                    temp_lagged_abnormalIdx = []
                    for j in range(min_ind, numRow):
                        temp_lagged_abnormalIdx.append(j)
                    lagged_abnormalIdx = temp_lagged_abnormalIdx
                lagged_abnormal_indexes.append(lagged_abnormalIdx)
        # print(lagged_abnormal_indexes)
        # detect lag for each attribute and adjust accordingly.
        if exp_param.find_lag:
            pass

        lagged_normal_matrix = []
        lagged_normal_matrix.append([])
        lagged_abnormal_matrix = []
        lagged_abnormal_matrix.append([])

        # get normal region for each attribute
        if exp_param.introduce_lag:
            lagged_normal_indexes.append([])
            for i in range(1, numAttr):
                lagged_normal_matrix_row = []
                lagged_abnormal_matrix_row = []
                if len(one_normal_regions) == 0:
                    normal_index = []
                    for j in range(0, numRow):
                        if (j not in lagged_abnormal_indexes[i]) and data[j][1] > 0:
                            normal_index.append(j)
                    lagged_normal_indexes.append(normal_index)

                else:
                    lagged_normal_indexes.append(one_normal_regions)
                for k in lagged_normal_indexes[i]:
                    lagged_normal_matrix_row.append(data[k])
                lagged_normal_matrix.append(lagged_normal_matrix_row)
                for k in lagged_abnormal_indexes[i]:
                    lagged_abnormal_matrix_row.append(data[k])
                lagged_abnormal_matrix.append(lagged_abnormal_matrix_row)
                # print("lagged_normal_matrix", len(lagged_normal_matrix[i]))

        # print(lagged_abnormal_matrix)
        if len(one_normal_regions) == 0:
            one_normal_regions = []
            for i in range(0, numRow):
                if (i not in one_abnormal_regions) and data[i][1] > 0:
                    one_normal_regions.append(i)

        # divide matrix into two regions
        normal_matrix = []
        abnormal_matrix = []
        for k in one_normal_regions:
            normal_matrix.append(data[k])
        for k in one_abnormal_regions:
            abnormal_matrix.append(data[k])

        lagged_training_data = []
        training_data = []
        rowCount = 0

        # note that we do not check for overlapping abnormal and normal regions.
        # training_data is for mining causal association rules
        for i in range(numRow):
            if i in one_abnormal_regions:
                temp = []
                temp.extend(data[i])
                temp.append(-1)  # -1 if abnormal
                training_data.append(temp)
                rowCount = rowCount + 1
            if i in normal_index:
                temp = []
                temp.extend(data[i])
                temp.append(1)  # 1 if normal
                training_data.append(temp)
                rowCount = rowCount + 1

        # some global variables for debugging
        global partitionLabels
        global partitionLabelsInitial
        global partitionLabelsAfterReset
        global numAlternatingPartitions
        global boundaries
        global myTemp
        global conflictCount
        global forcedNeutralCount

        normalPartitions = []
        abnormalPartitions = []
        partitionLabels = []
        partitionLabelsInitial = []
        partitionLabelsAfterReset = []
        numAlternatingPartitions = []
        conflictCount = []
        forcedNeutralCount = []

        attributeStatus = []
        normalizedNormalAverage = []
        normalizedAbnormalAverage = []

        normalAverage = []
        abnormalAverage = []
        categorical_predicates = []
        boundaries = []

        categorical_predicates.append([])
        boundaries.append([])
        partitionLabelsAfterReset.append([])
        normalPartitions.append([])
        abnormalPartitions.append([])
        normalizedNormalAverage.append(0)
        normalizedAbnormalAverage.append(0)
        forcedNeutralCount.append(0)
        partitionLabelsInitial.append([])
        partitionLabels.append([])
        normalAverage.append(0)
        abnormalAverage.append(0)
        conflictCount.append(0)
        temp_count = 0
        # Generate predicates using our predicate generation algorithm
        for i in range(1, numAttr):
            # print('i',i)
            temp_count = temp_count + 1
            # print("temp_count1",temp_count)
            if exp_param.introduce_lag:
                abnormalMatrix = lagged_abnormal_matrix[i]
                normalMatrix = lagged_normal_matrix[i]
                # print("normalMatrix",len(normalMatrix))
            else:
                abnormalMatrix = abnormal_matrix
                normalMatrix = normal_matrix
            # handle categorical attributes here
            if attribute_types[i] == categorical:
                categories_from_abnormal = (
                    np.unique(np.array(abnormalMatrix)[:, i]))
                categories_from_normal = np.unique(
                    np.array(normalMatrix)[:, i])
                categories = []
                categories.extend(categories_from_abnormal)
                categories.extend(categories_from_normal)
                category_predicate = []
                for c in range(len(categories)):
                    category = categories[c]
                    abnormal_count = np.count_nonzero(
                        np.array(abnormalMatrix)[:, i] == category)
                    normal_count = np.count_nonzero(
                        np.array(normalMatrix)[:, i] == category)
                    if abnormal_count > normal_count:
                        category_predicate.append(category)
                if len(category_predicate) > 0:
                    categorical_predicates.append(category_predicate)
                continue

            categorical_predicates.append([])
            conflictCount.append(0)
            # partitionLabels.append([])

            # creating a partition space
            maxValue = max(list(np.array(data)[:, i]))
            minValue = min(list(np.array(data)[:, i]))
            # print("filed_names",filed_names[i],maxValue,minValue)
            # print("data[i]",list(np.array(data)[:,i]))
            range1 = maxValue - minValue
            discrete_size = range1 / num_discrete
            if discrete_size == 0:
                boundaries.append([0 for index in range(num_discrete)])
            else:
                boundaries.append(
                    list(np.arange(minValue, maxValue, discrete_size)))
            boundary_count = len(boundaries[i])
            if boundary_count == 0:
                continue

            currentNormalPartitions = np.zeros((1, boundary_count))[0]
            currentAbnormalPartitions = np.zeros((1, boundary_count))[0]
            currentPartitionLabels = np.zeros((1, boundary_count))[0]
            current_boundary = boundaries[i]

            isConflict = False
            normalizedNormalSum = 0
            normalizedNormalCount = 0
            normalizedAbnormalSum = 0
            normalizedAbnormalCount = 0

            #localtime = time.asctime(time.localtime(time.time()))
            #print("localtime333", localtime)
            # partition labeling

            for j in range(len(current_boundary)):
                if j == len(current_boundary) - 1:
                    currentNormalPartitions[j] = np.sum(
                        np.array(normalMatrix)[:, i] >= current_boundary[j])
                    currentAbnormalPartitions[j] = np.sum(
                        np.array(abnormalMatrix)[:, i] >= current_boundary[j])
                else:
                    currentNormalPartitions1 = np.sum(
                        np.array(normalMatrix)[:, i] < current_boundary[j])
                    currentNormalPartitions2 = np.sum(
                        np.array(normalMatrix)[:, i] < current_boundary[j + 1])
                    currentNormalPartitions[j] = currentNormalPartitions2 - \
                        currentNormalPartitions1
                    currentAbnormalPartitions1 = np.sum(
                        np.array(abnormalMatrix)[:, i] < current_boundary[j])
                    currentAbnormalPartitions2 = np.sum(
                        np.array(abnormalMatrix)[:, i] < current_boundary[j + 1])
                    currentAbnormalPartitions[j] = currentAbnormalPartitions2 - \
                        currentAbnormalPartitions1

                if currentNormalPartitions[j] > 0 and currentAbnormalPartitions[j] > 0:
                    isConflict = True
                    conflictCount[i] = conflictCount[i] + 1
                    continue
                if currentNormalPartitions[j] > 0:
                    currentPartitionLabels[j] = abnormal_partition

                if isConflict:
                    if currentNormalPartitions[j] > currentAbnormalPartitions[j]:
                        currentPartitionLabels[j] = normal_partition
                    elif currentNormalPartitions[j] < currentAbnormalPartitions[j]:
                        currentPartitionLabels[j] = abnormal_partition
            #localtime = time.asctime(time.localtime(time.time()))
            #print("localtime444", localtime)

            # print(currentPartitionLabels)
            for j in range(len(current_boundary)):
                if currentPartitionLabels[j] == normal_partition:
                    normalizedNormalSum = normalizedNormalSum + \
                        ((current_boundary[j] - minValue) / range1)
                    normalizedNormalCount = normalizedNormalCount + 1

                elif currentPartitionLabels[j] == abnormal_partition:
                    normalizedAbnormalSum = normalizedAbnormalSum + \
                        ((current_boundary[j] - minValue) / range1)
                    normalizedAbNormalCount = normalizedAbnormalCount + 1

            # print(normalizedNormalSum, normalizedNormalCount)
            if normalizedNormalCount == 0:
                normalizedNormalAverage.append(0)
            else:
                normalizedNormalAverage.append(
                    normalizedNormalSum / normalizedNormalCount)
            if normalizedAbNormalCount == 0:
                normalizedAbnormalAverage.append(0)
            else:
                normalizedAbnormalAverage.append(
                    normalizedAbnormalSum / normalizedAbNormalCount)

            # pertition filtering
            markForNeutral = np.zeros((np.shape(currentPartitionLabels)))
            for j in range(len(currentPartitionLabels) - 1):
                currentPartition = currentPartitionLabels[j]
                if currentPartition == 0:
                    continue
                for k in range(j + 1, len(currentPartitionLabels)):
                    if currentPartitionLabels[k] > 0:
                        if currentPartitionLabels[k] != currentPartition:
                            markForNeutral[j] = 1
                            markForNeutral[k] = 1
                        break

            forcedNeutralCount.append(sum(markForNeutral))
            partitionLabelsInitial.append(currentPartitionLabels)

            normalCount = np.sum(
                np.array(currentPartitionLabels) == normal_partition)
            abnormalCount = np.sum(
                np.array(currentPartitionLabels) == abnormal_partition)

            for j in range(len(markForNeutral)):
                if markForNeutral[j] == 1:
                    if (currentPartitionLabels[j] == normal_partition) and (normalCount > 1):
                        currentPartitionLabels[j] = 0
                    elif (currentPartitionLabels[j] == abnormal_partition) and (abnormalCount > 1):
                        currentPartitionLabels[j] = 0
            partitionLabelsAfterReset.append(currentPartitionLabels)

            normalCount = np.sum(
                np.array(currentPartitionLabels) == normal_partition)
            abnormalCount = np.sum(
                np.array(currentPartitionLabels) == abnormal_partition)

            if normalCount == 0 and abnormalCount > 0:
                normalMean = np.mean(np.array(normalMatrix)[:, i])
                for j in range(len(current_boundary)):
                    if j == (len(current_boundary) - 1):
                        if normalMean >= current_boundary[j]:
                            currentPartitionLabels[j] = normal_partition
                            break
                    else:
                        if (normalMean >= current_boundary[j]) and (normalMean < current_boundary[j + 1]):
                            currentPartitionLabels[j] = normal_partition
                            break

            # filling the gap
            markForNeutral = np.zeros((np.shape(currentPartitionLabels)))
            for j in range(len(currentPartitionLabels)):
                if currentPartitionLabels[j] == 0:
                    distanceToNormal = num_discrete * 2 * abnormal_multiplier
                    distanceToAbnormal = num_discrete * 2 * abnormal_multiplier
                    k = j - 1
                    while k >= 0:
                        if currentPartitionLabels[k] == normal_partition:
                            if distanceToNormal > abs(k - j):
                                distanceToNormal = abs(k - j)
                            break
                        if currentPartitionLabels[k] == abnormal_partition:
                            if distanceToAbnormal > abs(k - j):
                                distanceToAbnormal = abs(
                                    k - j) * abnormal_multiplier
                            break
                        k = k - 1
                    k = j + 1
                    while k <= (len(currentPartitionLabels) - 1):
                        if (currentPartitionLabels[k]) == normal_partition:
                            if distanceToNormal > abs(k - j):
                                distanceToNormal = abs(k - j)
                            break
                        if currentPartitionLabels[k] == abnormal_partition:
                            if distanceToAbnormal > abs(k - j):
                                distanceToAbnormal = abs(
                                    k - j) * abnormal_multiplier
                            break
                        k = k + 1

                    if distanceToNormal < distanceToAbnormal:
                        markForNeutral[j] = normal_partition
                    elif distanceToAbnormal < distanceToNormal:
                        markForNeutral[j] = abnormal_partition

            for j in range(len(currentPartitionLabels)):
                if (currentPartitionLabels[j]) == 0:
                    currentPartitionLabels[j] = markForNeutral[j]

            normalPartitions.append(currentNormalPartitions)
            abnormalPartitions.append(currentAbnormalPartitions)
            partitionLabels.append(currentPartitionLabels)
            normalAverage.append(np.mean(np.array(normalMatrix)[:, i]))
            abnormalAverage.append(np.mean(np.array(abnormalMatrix)[:, i]))

        predicates = []
        temp_count = 0
        for i in range(1, numAttr):
            temp_count = temp_count + 1
            # print("temp_count2",temp_count)
            if len(partitionLabels[i]) == 0 or (np.sum(np.array(partitionLabels[i]) == abnormal_partition) == 0):
                continue

            partitions = partitionLabels[i]
            boundary = boundaries[i]
            # print('lenboundary')
            # print(len(boundary))
            predicateName = filed_names[i]
            if predicateName.find('dbmsCum') != -1:
                continue

            predicateString = ''
            predicateCount = 0
            lower = float('-inf')
            upper = float('inf')
            # print('lenpartitions')
            # print(len(partitions))
            for j in range(len(partitions) - 1):
                if j == 0 and partitions[j] == abnormal_partition:
                    predicateCount = predicateCount + 1
                if (partitions[j] != abnormal_partition) and (partitions[j + 1] == abnormal_partition):
                    if len(predicateString) != 0:
                        predicateString = predicateString + ' OR' + \
                            ' >' + str(round(boundary[j + 1], 6))
                    else:
                        # print("len(boundary)", len(boundary))
                        # print("j+1", j+1)
                        predicateString = ' > ' + \
                            str(round(boundary[j + 1], 6))
                    lower = boundary[j + 1]
                    predicateCount = predicateCount + 1
                elif (partitions[j] == abnormal_partition) and (partitions[j + 1] != abnormal_partition):
                    if len(predicateString) != 0:
                        predicateString = predicateString + ' and'
                    predicateString = predicateString + \
                        ' < ' + str(round(boundary[j + 1], 6))
                    upper = boundary[j + 1]
                    predicateCount = predicateCount + 1

            if len(predicateString) != 0:
                predicateString = predicateName + ' ' + predicateString

            if (predicateCount > 0 and predicateCount <= 2) or (
                    attribute_types[i] == categorical and len(categorical_predicates[i]) > 0):
                predicates.append([])
                predicates[-1].append(i)  # predicate index
                predicates[-1].append(predicateString)
                predicates[-1].append(attribute_types[i])  # predicate type
                predicates[-1].append(
                    abs(normalizedNormalAverage[i] - normalizedAbnormalAverage[i]))  # normalized avg. difference
                predicates[-1].append(lower)
                predicates[-1].append(upper)
                predicates[-1].append(categorical_predicates[i])
                predicates[-1].append(predicateName)
                predicates[-1].append(normalAverage[i])
                predicates[-1].append(abnormalAverage[i])

        prev_predicates = predicates
        # print('prev_predicates',prev_predicates)
        extra['num_should_be_filtered'] = 0
        extra['num_should_not_be_filtered'] = 0
        extra['num_filtered_correct'] = 0
        extra['before_false_positive'] = 0
        extra['before_false_negative'] = 0

        effect = []

        # create causal models from predicates after applying domain knowledge if it is enabled.
        if createModel:
            count = 1
            effectCount = 0
            extra['predicates_before'] = predicates
            if len(exp_param.domain_knowledge) != 0:
                predicates, c, incorrect, r, should_not_be_filtered, before_stat = filter_with_domain_knowledge(data,
                                                                                                                predicates,
                                                                                                                exp_param.domain_knowledge,
                                                                                                                exp_param.correct_filter_list)
                extra['num_filtered_correct'] = extra['num_filtered_correct'] + c
                extra['num_should_be_filtered'] = extra['num_should_be_filtered'] + r
                extra['num_filtered_incorrect'] = extra['num_filtered_incorrect'] + incorrect
                extra['num_should_not_be_filtered'] = extra['num_should_not_be_filtered'] + \
                    should_not_be_filtered
                extra['before_false_positive'] = extra['before_false_positive'] + \
                    before_stat['false_positive']
                extra['before_false_negative'] = extra['before_false_negative'] + \
                    before_stat['false_negative']

            sorted_predicates = []
            if len(predicates) > 0:
                sorted_predicates_temp = predicates
                # sorted_predicates_temp1 = predicates
                for k in list(np.argsort(np.array(sorted_predicates_temp, dtype=object)[:, 3])[::-1]):
                    sorted_predicates.append(sorted_predicates_temp[k])
                # print('sorted_predicates', sorted_predicates)
            for j in range(len(sorted_predicates)):
                if sorted_predicates[j][0] <= 0:
                    continue
                count = count + 1
                if sorted_predicates[j][3] > normalized_diff_threshold:
                    effect.append([])
                    effect[effectCount].append(
                        sorted_predicates[j][7])  # predicate name
                    # predicate type. (numeric or categorical)
                    effect[effectCount].append(sorted_predicates[j][2])
                    effect[effectCount].append(
                        [sorted_predicates[j][4], sorted_predicates[j][5]])
                    # category values for categorical attribute.
                    effect[effectCount].append(sorted_predicates[j][6])
                    effectCount = effectCount + 1

        model = {}
        model['predicates'] = effect
        # print("effect",effect)
        if len(modelName) == 0:
            # model_path = model_directory + '/' + ''.join(random.sample(string.ascii_letters + string.digits, 8))
            model_path = model_directory + '/' + ''.join('1')
        else:
            model_path = model_directory + '/' + modelName

        if createModel and len(sorted_predicates) > 0:
            model['cause'] = causeStr
            json.dump(model, open(model_path + ".txt", 'w'))

    print(filename + ' end: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    time_end = time.time()
    time_total += time_end - time_start
time_end_all = time.time()
print('total time: ' + str(time_total))
