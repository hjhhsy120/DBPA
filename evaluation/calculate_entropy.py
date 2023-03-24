import math


def calculate_entropy(p_x):
    e = 0
    total_x = 0
    if type(p_x[0]).__name__ == 'list':
        for i in range(len(p_x)):
            for j in range(len(p_x[0])):
                total_x = total_x + p_x[i][j]
    else:
        for i in p_x:
            total_x = total_x + i

    if type(p_x[0]).__name__ == 'list':
        for i in range(len(p_x)):
            for j in range(len(p_x[0])):
                p = p_x[i][j] / total_x
                if p != 0:
                    e = e + (p * math.log(p, 2))

    else:
        for i in p_x:
            p = i / total_x
            if p != 0:
                e = e + (p * math.log(p, 2))

    e = e * -1
    return e
