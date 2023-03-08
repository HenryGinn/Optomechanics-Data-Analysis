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

def get_file_contents(path):
    with open(path, "r") as file:
        file.readline()
        file_contents = [[float(value) for value in line.strip().split("\t")]
                         for line in file]
    return file_contents

def get_number_from_file_name(file_name, number_name):
    underscore_locations = get_underscore_locations(file_name, len(number_name))
    left_index = get_number_left_index(underscore_locations, file_name, number_name)
    right_index = get_number_right_index(left_index, file_name)
    number = get_number(file_name, left_index, right_index)
    return number

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

def get_number(file_name, left_index, right_index):
    try:
        number = float(file_name[left_index:right_index])
        return number
    except:
        could_not_convert_number_to_float_exception()

def could_not_convert_number_to_float_exception():
    raise Exception((f"Could not convert number to float\n"
                     f"File name: {file_name}\n"
                     f"left_index: {left_index}, right index: {right_index}"
                     f"{file_name[left_index:right_index]}\n"))

def get_last_number_in_file_name(file_name):
    underscore_locations = get_underscore_locations(file_name)
    left = underscore_locations[-1] + 1
    right = len(file_name) - 4
    last_number_in_file_name = file_name[left:right]
    return last_number_in_file_name
