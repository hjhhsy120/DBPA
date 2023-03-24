import numpy as np


def discretize_2d_continuous_variables(X, Y, bin_size):
    sizeX = len(X)
    sizeY = len(Y)
    bins = np.zeros((bin_size, bin_size))

    minX = min(X)
    maxX = max(X)
    rangeX = maxX - minX
    bin_edges_X = list(np.arange(minX, maxX, rangeX / bin_size))
    bin_index_X = []
    for i in range(len(X)):
        for j in range(len(bin_edges_X)):
            if j == len(bin_edges_X) - 1:
                bin_index_X.append(j)
            else:
                if (X[i] >= bin_edges_X[j]) and (X[i] < bin_edges_X[j + 1]):
                    bin_index_X.append(j)
                    break

    minY = min(Y)
    maxY = max(Y)
    rangeY = maxY - minY
    bin_edges_Y = list(np.arange(minY, maxY, rangeY / bin_size))
    bin_index_Y = []
    for i in range(len(Y)):
        for j in range(len(bin_edges_Y)):
            if j == len(bin_edges_Y) - 1:
                bin_index_Y.append(j)
            else:
                if (Y[i] >= bin_edges_Y[j]) and (Y[i] < bin_edges_Y[j + 1]):
                    bin_index_Y.append(j)
                    break

    for i in range(len(X)):
        bins[bin_index_X[i]][bin_index_Y[i]] = bins[bin_index_X[i]][bin_index_Y[i]] + 1

    return bins
