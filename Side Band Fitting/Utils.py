import os
import math

import numpy as np

def get_acceptable_indices(data, tolerance=4):
    if data.size < 3:
        acceptable_indices = np.arange(len(data))
    else:
        acceptable_indices = get_acceptable_indices_non_trivial(data, tolerance)
    return acceptable_indices

def get_acceptable_indices_non_trivial(data, tolerance):
    deviations = np.abs(data - np.median(data))
    modified_deviation = np.average(deviations**(1/4))**4
    accepted_indices = np.abs(deviations) < tolerance * modified_deviation
    return accepted_indices

def get_file_contents(path):
    with open(path, "r") as file:
        file.readline()
        file_contents = [[float(value) for value in line.strip().split("\t")]
                         for line in file]
    return file_contents

def get_data_from_file_name(file_name, data_name):
    underscore_locations = get_underscore_locations(file_name, len(data_name))
    left_index = get_number_left_index(underscore_locations, file_name, data_name)
    right_index = get_number_right_index(left_index, file_name)
    data = file_name[left_index:right_index]
    return data

def get_underscore_locations(file_name, limit=0):
    underscore_locations = [index for index, character in enumerate(file_name)
                            if character == "_" and index >= limit]
    return underscore_locations

def get_number_left_index(underscore_locations, file_name, number_name):
    try:
        number_left_index = [index for index in underscore_locations
                             if file_name[index - len(number_name):index] == number_name][0] + 1
        return number_left_index
    except:
        raise Exception(f"Could not find '{number_name}' in file name:\n{file_name}")

def get_number_right_index(left_index, file_name):
    right_index = left_index
    while is_index_valid(right_index, file_name):
        right_index += 1
    return right_index

def is_index_valid(index, file_name):
    is_number = (file_name[index] in "0123456789.-")
    is_not_at_end_of_file = (index < len(file_name) - 4)
    is_valid = is_number and is_not_at_end_of_file
    return is_valid

def get_number_from_file_name(file_name, number_name):
    number = get_data_from_file_name(file_name, number_name)
    number = get_number(number)
    return number

def get_number(number):
    try:
        number = float(number)
        return number
    except ValueError:
        raise ValueError(f"Could not convert {number} to float")

def get_last_number_in_file_name(file_name):
    underscore_locations = get_underscore_locations(file_name)
    left = underscore_locations[-1] + 1
    right = len(file_name) - 4
    last_number_in_file_name = file_name[left:right]
    return last_number_in_file_name

def make_folder(path, message=False):
    name = os.path.basename(path)
    if not os.path.isdir(path):
        if message:
            print(f"Making '{name}' folder at {path}")
        os.mkdir(path)

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

def get_number_from_string(string, number_type=float):
    try:
        return number_type(string)
    except TypeError:
        raise TypeError(f"Cannot convert {string} to {number_type}")

def get_group_indices(length, group_size):
    group_size, group_count = get_group_data(length, group_size)
    end_point_indices = get_end_point_indices(length, group_size, group_count)
    group_indices = [np.arange(end_point_indices[group_number],
                               end_point_indices[group_number + 1]).astype('int')
                     for group_number in range(group_count)]
    return group_indices

def get_group_data(length, group_size):
    group_size = set_group_size_non_none(length, group_size)
    group_size = get_modified_group_size(length, group_size)
    group_count = math.floor(length / group_size)
    return group_size, group_count

def set_group_size_non_none(length, group_size):
    if group_size is None:
        group_size = length
    return group_size

def get_modified_group_size(list_size, average_size):
    if list_size < average_size:
        average_size = list_size
    return average_size

def get_end_point_indices(length, group_size, group_count):
    real_group_size = length / group_count
    real_group_end_points = np.arange(0, group_count + 1) * real_group_size
    real_group_end_points = np.round(real_group_end_points, 5)
    end_point_indices = np.ceil(real_group_end_points)
    return end_point_indices

def get_moving_average(data, window_size=5):
    window = np.ones(window_size)
    numerator = np.convolve(data, window, "same")
    denominator = np.convolve(np.ones(len(data)), window, "same")
    moving_average = numerator / denominator
    return moving_average

def evaluate_lorentzian(x_values, lorentzian_parameters):
    F, gamma, noise, w = lorentzian_parameters
    function_values = (F/(gamma**2 + 4*(x_values - w)**2)) + noise
    return function_values
 
