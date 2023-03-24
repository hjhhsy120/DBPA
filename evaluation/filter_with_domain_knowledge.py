import numpy as np
from discretize_2d_continuous_variables import discretize_2d_continuous_variables
from calculate_entropy import calculate_entropy


def filter_with_domain_knowledge(data, predicates, domain_knowledge, correct_filter_list):
    num_attr = len(data[0]) - 2
    for i in range(len(domain_knowledge)):
        for j in range(len(domain_knowledge[i])):
            domain_knowledge[i][j] = domain_knowledge[i][j] + 2
    pred_index = np.array(predicates)[:, 0]
    pred_index_before = pred_index
    knowledge_size = len(domain_knowledge)

    predicates_to_filter = []
    predicates_not_to_filter = []
    correctly_filtered = []
    incorrectly_filtered = []

    num_filtered_required = 0
    num_filtered_not_required = 0
    num_filtered_correct = 0
    num_filtered_incorrect = 0

    # pred_index_before
    # correct_filter_list
    # pause

    for i in range(knowledge_size):
        knowledge = domain_knowledge[i]
        if len(knowledge) < 2:
            continue
        cause = knowledge[0]
        effects = knowledge[1:-1]

        # if cause variable is in the predicates...
        if len(list(set(pred_index).intersection(set[cause]))) != 0:
            pred_to_filter = []
            for j in range(len(effects)):
                effect = effects[j]
                # if effect variable is also in the predicates...
                if len(list(set(pred_index).intersection(set([effect])))) != 0:
                    p_xy = discretize_2d_continuous_variables(np.array(data)[:, cause], np.array(data)[:, effect], 100)
                    p_x = []
                    for x in range(len(p_xy)):
                        pxy = 0
                        for row in p_xy[x]:
                            pxy = row + pxy
                        p_x.append(pxy)
                    p_y = []
                    for y in range(len(p_xy[0])):
                        pxy = 0
                        for column in np.array(p_xy)[:,y]:
                            pxy = column + pxy
                        p_y.append(pxy)

                    entropy_x = calculate_entropy(p_x)
                    entropy_y = calculate_entropy(p_y)
                    entropy_xy = calculate_entropy(p_xy)

                    mutual_information = entropy_x + entropy_y - entropy_xy
                    mutual_info_gain = (mutual_information ** 2) / (entropy_x * entropy_y)
                    if mutual_info_gain > 0:
                        pred_to_filter.append(effect)

            if len(correct_filter_list) != 0:
                filter_index = []
                for k in range(len(np.array(correct_filter_list)[:,0])):
                    if correct_filter_list[k][0] + 2 == cause:
                        filter_index.append(k)
                correct_list = []
                for k in filter_index:
                    correct_list.append(correct_filter_list[k][1])
                incorrect_list = []
                for k in filter_index:
                    incorrect_list.append(correct_filter_list[k][2])
                predicates_to_filter = predicates_to_filter.extend(correct_list)
                predicates_not_to_filter = predicates_not_to_filter.extend(incorrect_list)
                for k in range(len(correct_list)):
                    correct_list[k] = correct_list[k] + 2
                for k in range(len(incorrect_list)):
                    incorrect_list[k] = incorrect_list[k] + 2

                filtered_correctly = list(set(correct_list).intersection(set(pred_to_filter)))
                filtered_incorrectly = list(set(incorrect_list).intersection(set(pred_to_filter)))

                if len(correctly_filtered) == 0:
                    correctly_filtered = filtered_correctly
                else:
                    correctly_filtered.extend(filtered_correctly)

                if len(incorrectly_filtered) == 0:
                    incorrectly_filtered = filtered_incorrectly
                else:
                    incorrectly_filtered.extend(filtered_incorrectly)

            for j in range(len(pred_to_filter)):
                index = pred_to_filter[j]
                index_to_filter = []
                for k in range(len(pred_index)):
                    if pred_index[k] == index:
                        index_to_filter.append(k)
                for k in index_to_filter:
                    for l in range(len(predicates[k])):
                        predicates[k][l] = 0
                pred_index = np.array(predicates)[:, 0]

    predicates_to_filter = np.unique(predicates_to_filter)
    if len(correctly_filtered) == 0:
        num_filtered_correct = 0
    else:
        num_filtered_correct = len(np.unique(correctly_filtered))
    if len(incorrectly_filtered) == 0:
        num_filtered_correct = 0
    else:
        num_filtered_incorrect = len(np.unique(incorrectly_filtered))

    for k in predicates_to_filter:
        if k > 0:
            num_filtered_required = num_filtered_required + 1

    if len(predicates_not_to_filter) == 0:
        num_filtered_not_required = 0
    else:
        num_filtered_not_required = len(np.unique(predicates_not_to_filter))

    new_predicates = predicates
    before_stat = {}

    before_filtered = []
    A_temp = np.arange(2, num_attr + 1, 1)
    for a in A_temp:
        if a not in pred_index_before:
            before_filtered.append(a)
    for k in predicates_to_filter:
        if k == 0:
            predicates_to_filter.remove(k)
    for k in predicates_not_to_filter:
        if k == 0:
            predicates_not_to_filter.remove(k)

    pred_index_before[:] = [x - 2 for x in pred_index_before]
    before_stat['false_negative'] = len(np.unique(list(set(pred_index_before).intersection(set(predicates_to_filter)))))
    before_stat['false_positive'] = len(np.unique(list(set(before_filtered).intersection(set(predicates_not_to_filter)))))

    return new_predicates, num_filtered_correct, num_filtered_incorrect, num_filtered_required, num_filtered_not_required, before_stat
