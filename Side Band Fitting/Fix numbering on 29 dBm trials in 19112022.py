import os
import sys
import shutil

def fix_names():
    data_set_path_spectrum = os.path.join(data_set_path, "19112022", "Spectrum", "29")
    data_set_path_transmission = os.path.join(data_set_path, "19112022", "Transmission", "29")
    fix_trial_folders(data_set_path_spectrum)
    fix_trial_folders(data_set_path_transmission)

def fix_trial_folders(path):
    delete_trial_0(path)
    for trial_folder_name in sorted(os.listdir(path), key=lambda x: int(x[3:])):
        update_path(path, trial_folder_name)

def delete_trial_0(path):
    trial_0_path = os.path.join(path, "29_0")
    if os.path.exists(trial_0_path):
        print("Deleting trial 0")
        shutil.rmtree(trial_0_path)

def update_path(trial_folder_path, trial_folder_name):
    original_trial_folder_path = os.path.join(trial_folder_path, trial_folder_name)
    number = int(trial_folder_name[3:])
    new_trial_folder_name = f"{trial_folder_name[0:3]}{number - 1}"
    new_trial_folder_path = os.path.join(trial_folder_path, new_trial_folder_name)
    os.rename(original_trial_folder_path, new_trial_folder_path)

input(("Warning: you must have run 'PutTrialsInFolders' before running the program\n"
       "Press enter to continue running the program if you have done this\n"))

data_set_path = "D:\\Documents\\Experiments\\RT_exp4"

fix_names()
