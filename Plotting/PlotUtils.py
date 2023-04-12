import math

import numpy as np
import matplotlib.pyplot as plt

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

def get_group_size(group_size, object_list):
    if group_size is None:
        group_size = len(object_list)
    return group_size

def get_group_indexes(length, group_size):
    group_size, group_count = get_group_data(length, group_size)
    end_point_indexes = get_end_point_indexes(length, group_size, group_count)
    group_indexes = construct_group_indexes(length, group_count, end_point_indexes)
    return group_indexes

def get_group_data(length, group_size):
    group_size = get_modified_group_size(length, group_size)
    group_count = math.floor(length/group_size)
    return group_size, group_count

def get_modified_group_size(list_size, average_size):
    if list_size < average_size:
        average_size = list_size
    return average_size

def get_end_point_indexes(length, group_size, group_count):
    real_group_size = length/group_count
    real_group_end_points = np.arange(0, group_count + 1) * real_group_size
    real_group_end_points = np.round(real_group_end_points, 5)
    end_point_indexes = np.ceil(real_group_end_points)
    return end_point_indexes

def construct_group_indexes(length, group_count, end_point_indexes):
    group_indexes = [np.arange(end_point_indexes[group_number],
                               end_point_indexes[group_number + 1]).astype('int')
                     for group_number in range(group_count)]
    return group_indexes

def update_figure_size(width=10, height=6):
    plt.gcf().set_size_inches(width, height)

def adjust_subplots(bottom=0.1, top=0.9,
                    left=0.05, right=0.95,
                    wspace=0.3, hspace=0.3):
    plt.gcf().subplots_adjust(bottom=bottom, top=top,
                              right=right, left=left,
                              wspace=wspace, hspace=hspace)

def get_prefixed_numbers(numbers):
    powers_of_1000 = [get_power_of_1000(abs(number)) for number in numbers
                      if number != 0]
    power_of_1000 = min(powers_of_1000)
    prefix = get_prefix(power_of_1000)
    numbers = [int(number / 1000**power_of_1000) for number in numbers]
    return numbers, prefix

def get_power_of_1000(input_number):
    power_of_1000 = np.log(input_number) / np.log(1000)
    power_of_1000 = np.floor(np.round(power_of_1000, 5))
    return power_of_1000

def get_prefix(power_of_1000):
    prefix_dict = {-5: "f", -4: "n", -3: "$\mu$", -2: "m", 0: "",
                   1: "k", 2: "M", 3: "G", 4: "T", 5: "P"}
    prefix = prefix_dict[power_of_1000]
    return prefix
