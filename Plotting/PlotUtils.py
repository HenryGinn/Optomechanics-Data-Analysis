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

def update_figure_size(width=8, height=4.8):
    plt.gcf().set_size_inches(width, height)
    plt.gca().set_position([0, 0, 1, 1])
    plt.gcf().subplots_adjust(top=0.92)
    plt.tight_layout()


def get_pretty_axis(limits):
    limits = round_limits(limits)
    limits, offset = get_axis_offset(limits)
    tick_positions = np.array(limits)
    tick_labels, prefix = get_prefixed_numbers(tick_positions)
    return tick_positions, tick_labels, offset, prefix

def round_limits(limits):
    lower_limit, upper_limit = limits
    lower_limit = floor(lower_limit, -1)
    upper_limit = ceil(upper_limit, -1)
    return (lower_limit, upper_limit)

def floor(number, significance):
    magnitude = get_magnitude(abs(number))
    rounded = round(abs(number), -significance - magnitude)
    if abs(number) - rounded < 0:
        number = np.sign(number)*rounded - 10**(magnitude + significance)
    return number

def ceil(number, significance):
    magnitude = get_magnitude(abs(number))
    rounded = round(abs(number), -significance - magnitude)
    if abs(number) - rounded > 0:
        number = np.sign(number)*rounded + 10**(magnitude + significance)
    return number

def get_axis_offset(limits):
    average = sum(limits) / 2
    offset = 0
    if average != 0:
        difference_magnitude = get_magnitude(limits[1] - limits[0])
        average_magnitude = get_magnitude(abs(average))
        limits, offset = offset_limits(limits, difference_magnitude, average_magnitude)
    return limits, offset

def get_magnitude(input_number):
    log = round(math.log(input_number, 10), 2)
    magnitude = math.floor(log)
    return magnitude

def offset_limits(limits, difference_magnitude, average_magnitude):
    offset = 0
    if difference_magnitude < average_magnitude - 1:
        offset = limits[0]
        limits = [limits[0] - offset, limits[1] - offset]
    return limits, offset

def get_prefixed_numbers(numbers):
    powers_of_1000 = [get_power_of_1000(abs(number)) for number in numbers]
    power_of_1000 = min(powers_of_1000)
    prefix = get_prefix(power_of_1000)
    numbers = np.around(numbers / 1000**power_of_1000)
    return numbers, prefix

def get_prefixed_number(input_number):
    power_of_1000 = get_power_of_1000(input_number)
    prefix = get_prefix(power_of_1000)
    base_number = input_number / 1000**power_of_1000
    prefixed_number = f"{round(base_number)}{prefix}"
    return prefixed_number

def get_power_of_1000(input_number):
    power_of_1000 = np.log(input_number) / np.log(1000)
    power_of_1000 = np.floor(np.round(power_of_1000, 5))
    return power_of_1000

def get_prefix(power_of_1000):
    prefix_dict = {-5: "f", -4: "n", -3: "$\mu$", -2: "m", 0: "",
                   1: "k", 2: "M", 3: "G", 4: "T", 5: "P"}
    prefix = prefix_dict[power_of_1000]
    return prefix
