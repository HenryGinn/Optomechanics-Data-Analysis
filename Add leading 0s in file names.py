import os
import sys
import glob

def iterate_through_power_levels_1(data_set):
    path = os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), data_set)
    for power_folder in os.listdir(path):
        files = get_files_1(data_set, power_folder)
        for file in files:
            fix_file_name(file)

def iterate_through_power_levels_2(data_set):
    path = os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), data_set, "Spectrum")
    for power_folder in os.listdir(path):
        files = get_files_2(data_set, power_folder)
        for file in files:
            fix_file_name(file)

def get_files_1(data_set, power_folder):
    parent_folder = os.path.dirname(os.path.dirname(sys.path[0]))
    path = os.path.join(parent_folder, data_set, power_folder, "Spectrum")
    os.chdir(path)
    files= glob.glob('*.txt')
    return files

def get_files_2(data_set, power_folder):
    parent_folder = os.path.dirname(os.path.dirname(sys.path[0]))
    power_folder_path = os.path.join(parent_folder, data_set, "Spectrum", power_folder)
    files = []
    for folder in os.listdir(power_folder_path):
        path = os.path.join(power_folder_path, folder)
        for file in os.listdir(path):
            files.append(os.path.join(power_folder_path, folder, file))
    return files

def fix_file_name(file):
    underscore_locations = [index for index, character in enumerate(file) if character == "_"]
    left_index = underscore_locations[-2] + 1
    right_index = underscore_locations[-1]
    group_count = file[left_index:right_index]
    if len(group_count) == 1:
        new_file_name = f"{file[:left_index]}0{group_count}{file[right_index:]}"
        os.rename(file, new_file_name)

#data_set = "15112022"
data_set = "16112022_overnight"
iterate_through_power_levels_2(data_set)
