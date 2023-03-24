import numpy as np
import random
from filter_with_domain_knowledge import filter_with_domain_knowledge
from loadCausalModels_Combiner import loadCausalModels_NotCombiner
from sklearn.metrics import accuracy_score,precision_recall_fscore_support
import pickle
import time
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


faultlist = ['fault1_data', 'fault2_data', 'fault3_data', 'fault4_data', 'fault5_data', 'multiindex_data', 'setknob_data', 'stress_data', 'lockwait_data']

parser = argparse.ArgumentParser(description='Arguments from CMD')
parser.add_argument('--data_cnt', type=int, default=40, help='data_cnt')
parser.add_argument('--head_file', type=str,default='head.txt', help='head_file')
args = parser.parse_args()
head_file = args.head_file
data_cnt = args.data_cnt

datafolder = './dbsherlock_data/faultdata_'+str(data_cnt)+'/'
model_directory = './dbsherlock_model/causal_model_'+str(data_cnt)
causalModels = loadCausalModels_NotCombiner(model_directory)
cnt = 0
data = []
label = []
pred = []
for filename in faultlist:
    f = open(datafolder+filename+'.pickle','rb')
    _ , data1 = pickle.load(f)
    label1 = [filename] * len(data1)
    data += data1
    label += label1
correct_count = 0
total_count = 0
time_start = time.time()
for num in range(len(data)):
    one_test_datasets = data[num][0]
    if isinstance(data[num][1], str):
        # print("label111", data[num][1])
        one_abnormal_regions = np.arange(12, len(one_test_datasets), 1)
    elif isinstance(data[num][1], list) and len(data[num][1]) == 1:
        # print("label222", data[num][2])
        one_abnormal_regions = np.arange(
            data[num][1][0], data[num][1][0] + 12, 1)
    else:
        # print("label333", data[num][2])
        one_abnormal_regions = np.arange(
            data[num][1][0], data[num][1][1] + 1, 1)
    exp_param = ExperimentParameter()
    one_normal_regions = []
    attribute_types = []
    data1 = one_test_datasets 
    for i in range(len(data1)):
        data1[i][0] = 1

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
    numRow = len(data1)
    numAttr = len(data1[0])
    if len(attribute_types) == 0:
        attribute_types = np.zeros((1, numAttr))[0]
        attribute_types = attribute_types.tolist()
    num_discrete = exp_param.num_discrete
    normalized_diff_threshold = exp_param.diff_threshold
    abnormal_multiplier = exp_param.abnormal_multiplier
    createModel = exp_param.create_model
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
                    if (j not in lagged_abnormal_indexes[i]) and data1[j][1] > 0:
                        normal_index.append(j)
                lagged_normal_indexes.append(normal_index)
            else:
                lagged_normal_indexes.append(one_normal_regions)
            for k in lagged_normal_indexes[i]:
                lagged_normal_matrix_row.append(data1[k])
            lagged_normal_matrix.append(lagged_normal_matrix_row)
            for k in lagged_abnormal_indexes[i]:
                lagged_abnormal_matrix_row.append(data1[k])
            lagged_abnormal_matrix.append(lagged_abnormal_matrix_row)
            # print("lagged_normal_matrix", len(lagged_normal_matrix[i]))
    # print(lagged_abnormal_matrix)
    if len(one_normal_regions) == 0:
        
        one_normal_regions = []
        for i in range(0, numRow):
            if (i not in one_abnormal_regions) and data1[i][1] > 0:
                one_normal_regions.append(i)
    # divide matrix into two regions
    normal_matrix = []
    abnormal_matrix = []
    for k in one_normal_regions:
        normal_matrix.append(data1[k])
    for k in one_abnormal_regions:
        abnormal_matrix.append(data1[k])
    lagged_training_data = []
    training_data = []
    rowCount = 0
    # note that we do not check for overlapping abnormal and normal regions.
    # training_data is for mining causal association rules
    for i in range(numRow):
        if i in one_abnormal_regions:
            temp = []
            temp.extend(data1[i])
            temp.append(-1)  # -1 if abnormal
            training_data.append(temp)
            rowCount = rowCount + 1
        if i in normal_index:
            temp = []
            temp.extend(data1[i])
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
        # creating a partition space
        maxValue = max(list(np.array(data1)[:, i]))
        minValue = min(list(np.array(data1)[:, i]))
        # print("filed_names",filed_names[i],maxValue,minValue)
        # print("data1[i]",list(np.array(data1)[:,i]))
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
                    # print("len(boundary)",len(boundary))
                    # print("j+1",j+1)
                    predicateString = str(round(boundary[j + 1], 6))
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
            predicates, c, incorrect, r, should_not_be_filtered, before_stat = filter_with_domain_knowledge(data1,
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
            for k in list(np.argsort(np.array(sorted_predicates_temp,dtype=object)[:, 3])[::-1]):
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
    # print("len(causalModels)",len(causalModels))
    # print("lencausalModels",len(causalModels))
    causeRank = []
    '''
        for i in range(2, len(boundaries)):
            if boundaries[i][0] != 0:
                print(i)
        '''
    # print("boundaries",boundaries)
    for i in range(len(causalModels)):
        cause = causalModels[i]['cause']
        effectPredicates = causalModels[i]['predicates']
        coveredAbnormalRatioAverage = 0
        coveredNormalRatioAverage = 0
        precisionAverage = 0
        recallAverage = 0
        for j in range(len(effectPredicates)):
            # print("effectPredicates",effectPredicates)
            field = effectPredicates[j][0]
            # print("field1111111",field)
            fieldIndex = -1
            for k in range(len(filed_names)):
                if filed_names[k] == field:
                    fieldIndex = k
                    break
            # print("fieldIndex",fieldIndex)
            if fieldIndex == -1:
                print('the field: ' + str(field) + ' not found!')
                continue
            if effectPredicates[j][1] == numeric:
                predicate = effectPredicates[j][2]
            elif effectPredicates[j][1] == categorical:
                predicate = effectPredicates[j][3]
            if attribute_types[fieldIndex] == numeric:
                currentPartition = partitionLabelsInitial[fieldIndex]
                # print("fieldIndex1111111",fieldIndex)
                partitionBoundaries = boundaries[fieldIndex]
                # print("boundaries[fieldIndex]",boundaries[fieldIndex])
                normalPartitionCount = 0
                abnormalPartitionCount = 0
                coveredPartitionCount = 0
                coveredNormalCount = 0
                # print("currentPartition",currentPartition)
                for k in range(len(currentPartition)):
                    if currentPartition[k] == abnormal_partition:
                        abnormalPartitionCount = abnormalPartitionCount + 1
                        for p in range(len(predicate)):
                            lower = predicate[0]
                            upper = predicate[1]
                            if k <= len(currentPartition) - 2:
                                if lower != float('-inf') and lower > partitionBoundaries[k]:
                                    continue
                                elif upper != float('inf') and k != len(currentPartition) and upper <= \
                                        partitionBoundaries[k + 1]:
                                    continue
                            else:
                                continue
                            coveredPartitionCount = coveredPartitionCount + 1
                            break
                    elif currentPartition[k] == normal_partition:
                        normalPartitionCount = normalPartitionCount + 1
                        for p in range(len(predicate)):
                            lower = predicate[0]
                            upper = predicate[1]
                            if k <= len(currentPartition) - 2:
                                if lower != float('-inf') and lower > partitionBoundaries[k]:
                                    continue
                                elif upper != float('inf') and k != len(currentPartition) and upper <= \
                                        partitionBoundaries[k + 1]:
                                    continue
                            else:
                                continue
                            coveredNormalCount = coveredNormalCount + 1
                            # print("coveredNormalCount",coveredNormalCount)
                            break
                if abnormalPartitionCount == 0:
                    ratio = 0
                else:
                    ratio = (coveredPartitionCount /
                             abnormalPartitionCount)
                coveredAbnormalRatioAverage = coveredAbnormalRatioAverage + ratio
                if normalPartitionCount == 0:
                    ratio = 0
                else:
                    ratio = (coveredNormalCount / normalPartitionCount)
                coveredNormalRatioAverage = coveredNormalRatioAverage + ratio
                if (coveredNormalCount + coveredPartitionCount) == 0:
                    ratio = 0
                else:
                    ratio = (coveredPartitionCount /
                             (coveredNormalCount + coveredPartitionCount))
                precisionAverage = precisionAverage + ratio
            elif attribute_types[fieldIndex] == categorical:
                normalCount = len(normalMatrix)
                abnormalCount = len(abnormalMatrix)
                cNC = 0
                for k in predicate:
                    for l in np.array(normalMatrix)[:, fieldIndex]:
                        if k == l:
                            cNC = cNC + 1
                coveredNormalCount = cNC
                cAC = 0
                for k in predicate:
                    for l in np.array(abnormalMatrix)[:, fieldIndex]:
                        if k == l:
                            cAC = cAC + 1
                coveredAbnormalCount = cAC
                if abnormalCount == 0:
                    ratio = 0
                else:
                    ratio = (coveredAbnormalCount / abnormalCount)
                coveredAbnormalRatioAverage = coveredAbnormalRatioAverage + ratio
                if normalCount == 0:
                    ratio = 0
                else:
                    ratio = (coveredNormalCount / normalCount)
                coveredNormalRatioAverage = coveredNormalRatioAverage + ratio
                if (coveredNormalCount + coveredAbnormalCount) == 0:
                    ratio = 0
                else:
                    ratio = (coveredAbnormalCount /
                             (coveredNormalCount + coveredAbnormalCount))
                precisionAverage = precisionAverage + ratio
        # print("effectPredicates", effectPredicates)
        if len(effectPredicates) == 0:
            coveredAbnormalRatioAverage = 0
            coveredNormalRatioAverage = 0
            precisionAverage = 0
        else:
            coveredAbnormalRatioAverage = coveredAbnormalRatioAverage / \
                len(effectPredicates)
            coveredNormalRatioAverage = coveredNormalRatioAverage / \
                len(effectPredicates)
            precisionAverage = precisionAverage / len(effectPredicates)
        causeRank.append([])
        causeRank[i].append(cause)
        causeRank[i].append(
            (coveredAbnormalRatioAverage - coveredNormalRatioAverage) * 100)  # confidence
        causeRank[i].append(precisionAverage * 100)  # precision
        if (coveredAbnormalRatioAverage + precisionAverage) == 0:
            causeRank[i].append(0)
        else:
            causeRank[i].append(2 * (coveredAbnormalRatioAverage * precisionAverage) / (
                coveredAbnormalRatioAverage + precisionAverage) * 100)  # f1-measure
        causeRank[i].append(coveredAbnormalRatioAverage * 100)  # recall
    if len(causeRank) != 0:
        causeRank_temp = causeRank
        # causeRank_temp1 = causeRank
        causeRank = []
        for k in list(np.argsort(np.array(causeRank_temp,dtype=object)[:, 1])[::-1]):
            causeRank.append(causeRank_temp[k])
    explanation = causeRank
    total_count += 1
    fault1 = 0
    fault2 = 0
    fault3 = 0
    fault4 = 0
    fault5 = 0
    lock = 0
    stress = 0
    multi = 0
    setknob = 0
    for i in range(0, min(len(explanation),20)):
        if explanation[i][0] == "fault1_data":
            fault1 += 1
        elif explanation[i][0] == "fault2_data":
            fault2 += 1
        elif explanation[i][0] == "fault3_data":
            fault3 += 1
        elif explanation[i][0] == "fault4_data":
            fault4 += 1
        elif explanation[i][0] == "fault5_data":
            fault5 += 1
        elif explanation[i][0] == "multiindex_data":
            multi += 1
        elif explanation[i][0] == "setknob_data":
            setknob += 1
        elif explanation[i][0] == "stress_data":
            stress += 1
        elif explanation[i][0] == "lockwait_data":
            lock += 1
    aa = [fault1, fault2, fault3, fault4, fault5, multi, setknob, stress,lock]
    pred.append(faultlist[aa.index(max(aa))])
    fault_cnt = int(data_cnt*0.3)
    if len(pred)%fault_cnt==0:
        print(faultlist[cnt] + ' Acc:{}'.format(accuracy_score(label[cnt*fault_cnt:cnt*fault_cnt+fault_cnt], pred[cnt*fault_cnt:cnt*fault_cnt+fault_cnt])))
        # print(label[cnt*fault_cnt:cnt*fault_cnt+fault_cnt])
        # print(label[cnt*fault_cnt+fault_cnt])
        # print(pred[cnt*fault_cnt:cnt*fault_cnt+fault_cnt])
        cnt += 1
time_end = time.time()
print('pred time: ' + str(time_end-time_start))
predresult = label,pred
f = open('predresult_'+str(data_cnt)+'.pkl','wb')
pickle.dump(predresult,f)
f.close()
print('{:<10}\tAcc = {:.4f}'.format('DBS',accuracy_score(label, pred)))
results = precision_recall_fscore_support(
    label, pred, labels=faultlist, average=None)
for j in range(9):
    print('{:<10}\t{},{},{}'.format(faultlist[j], results[0][j], results[1][j], results[2][j]))