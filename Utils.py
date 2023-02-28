import numpy as np

def get_acceptable_indexes(data, tolerance=4):
    if data.size < 3:
        acceptable_indexes = np.arange(len(data))
    else:
        acceptable_indexes = get_acceptable_indexes_non_trivial(data, tolerance)
    return acceptable_indexes

def get_acceptable_indexes_non_trivial(data, tolerance):
    deviations = np.abs(data - np.median(data))
    modified_deviation = np.average(deviations**(1/4))**4
    accepted_indexes = np.abs(deviations) < tolerance * modified_deviation
    return accepted_indexes
