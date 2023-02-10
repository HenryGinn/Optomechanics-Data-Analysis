import os
import sys
import shutil

def put_trials_in_folders(folder_name):
    script_path = sys.path[0]
    parent_path = os.path.dirname(os.path.dirname(script_path))
    data_set_path = os.path.join(parent_path, "Data Sets", folder_name)
    process_folder(data_set_path, "Spectrum")
    process_folder(data_set_path, "Transmission")

def process_folder(data_set_path, data_type):
    data_type_path = os.path.join(data_set_path, data_type)
    if folder_broken(data_type_path):
        input("Folder names are broken: press enter to fix them")
        fix_folders(data_type_path)

def folder_broken(data_type_path):
    if len(os.listdir(data_type_path)) != 0:
        folder_name = os.listdir(data_type_path)[0]
        if len(folder_name) != 2:
            if "." not in folder_name:
                return True
            else:
                return False
        return False

def fix_folders(data_type_path):
    powers = list(set([folder_name[:2] for folder_name in os.listdir(data_type_path)]))
    create_folders(data_type_path, powers)
    move_folders(data_type_path)

def create_folders(data_type_path, powers):
    for power in powers:
        power_path = os.path.join(data_type_path, power)
        if os.path.isdir(power_path) == False:
            os.mkdir(power_path)

def move_folders(data_type_path):
    for folder_name in os.listdir(data_type_path):
        if len(folder_name) != 2:
            new_folder_name = get_new_folder_name(folder_name)
            old_folder_path = os.path.join(data_type_path, folder_name)
            new_folder_path = os.path.join(data_type_path, folder_name[:2], new_folder_name)
            shutil.move(old_folder_path, new_folder_path)

def get_new_folder_name(folder_name):
    power = folder_name[:2]
    if "_" in folder_name:
        trial = folder_name[3:]
    else:
        trial = folder_name[2:]
    new_folder_name = f"{power}_{trial}"
    return new_folder_name
