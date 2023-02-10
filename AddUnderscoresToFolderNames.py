import os
import sys

def fix_names(folder_name):
    script_path = sys.path[0]
    parent_path = os.path.dirname(os.path.dirname(script_path))
    data_set_path_spectrum = os.path.join(parent_path, "Data Sets", folder_name, "Spectrum")
    data_set_path_transmission = os.path.join(parent_path, "Data Sets", folder_name, "Transmission")
    iterate_through_power_folders(data_set_path_spectrum)
    iterate_through_power_folders(data_set_path_transmission)

def iterate_through_power_folders(path):
    for power_folder_name in os.listdir(path):
        power_folder_path = os.path.join(path, power_folder_name)
        for trial_folder_name in os.listdir(power_folder_path):
            update_path(power_folder_path, trial_folder_name)

def update_path(power_folder_path, trial_folder_name):
    original_trial_folder_path = os.path.join(power_folder_path, trial_folder_name)
    if trial_folder_name[2] != "_":
        trial_folder_name = f"{trial_folder_name[0:2]}_{trial_folder_name[2:]}"
    new_trial_folder_path = os.path.join(power_folder_path, trial_folder_name)
    os.rename(original_trial_folder_path, new_trial_folder_path)

def add_underscore_to_folder_names(folder_name):
    input(("Warning: you must put each of the sets of trials into folders '27', '28', '29' beforehand\n"
           "Make sure you have done this for transmission and spectrum folders\n"
           "Press enter to continue running the program if you have done this\n"))
    fix_names(folder_name)
    
