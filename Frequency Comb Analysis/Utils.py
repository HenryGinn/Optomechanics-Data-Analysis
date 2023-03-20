import math

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

def get_file_contents_from_path(path):
    with open(path, "r") as file:
        file.readline()
        file_contents = get_file_contents_from_file(file, path)
        file_contents = [np.array(column) for column in zip(*file_contents)]
    return file_contents

def get_file_contents_from_file(file, path):
    try:
        return [[get_number_from_string(value) for value in line.strip().split("\t")]
                for line in file]
    except:
        raise Exception(f"An error occured when extracting data from {path}")

def get_number_from_file_name(string_to_find, file_name, offset=1, number_type=float):
    substrings = get_substrings(string_to_find, file_name)
    if string_to_find not in substrings:
        return None
    else:
        return get_number_from_substrings(string_to_find, file_name, substrings, offset, number_type)

def get_substrings(string_to_find, file_name):
    substrings = [file_name[index:index + len(string_to_find)]
                  for index in range(len(file_name) - len(string_to_find))]
    return substrings

def get_number_from_substrings(string_to_find, file_name, substrings, offset, number_type):
    left_index = substrings.index(string_to_find) + len(string_to_find) + offset
    right_index = get_right_index(file_name, left_index)
    number = number_type(file_name[left_index:right_index])
    return number

def get_right_index(file_name, left_index):
    right_index = left_index
    while is_index_valid(right_index, file_name):
        right_index += 1
    return right_index

def is_index_valid(index, file_name):
    is_number = (file_name[index] in "0123456789.-")
    is_not_at_end_of_file = (index < len(file_name) - 4)
    is_valid = is_number and is_not_at_end_of_file
    return is_valid

def get_file_contents(file, file_name):
    file_contents = [process_line(line, file_name) for line in file]
    file_contents = [np.array(column) for column in zip(*file_contents)]
    return file_contents

def process_line(line, file_name):
    line = line.strip().split("\t")
    line = [convert_to_float(number, file_name) for number in line]
    return line

def convert_to_float(number, file_name):
    try:
        number = float(number)
    except:
        raise Exception(f"Cannot convert {number} to float in file:\n"
                        f"{file_name}")
    return number

def convert_to_milliwatts(voltage):
    milliwatts = (10**(voltage / 10)) / 1000
    return milliwatts

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

def get_number_from_string(string, number_type=float):
    try:
        return number_type(string)
    except TypeError:
        raise TypeError(f"Cannot convert {string} to {number_type}")
