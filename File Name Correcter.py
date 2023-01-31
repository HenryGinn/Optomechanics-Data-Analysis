import os

def get_rejected_indices(underscore_locations):
    stop_location = underscore_locations[3] + 5
    start_location = underscore_locations[4]
    rejected_indices = range(stop_location, start_location)
    return rejected_indices

def rename_file(old_name, new_name):
    old_path = os.path.join(os.getcwd(), "Transmission", old_name)
    new_path = os.path.join(os.getcwd(), "Transmission", new_name)
    os.rename(old_path, new_path)

path = os.path.join(os.getcwd(), "Transmission")
file_list = os.listdir(path)

for file in file_list:
    underscore_locations = [index for index, character in enumerate(file)
                            if character == "_"]
    rejected_indices = get_rejected_indices(underscore_locations)
    new_file_name = "".join([file[i] for i in range(len(file))
                             if i not in rejected_indices])
    rename_file(file, new_file_name)
    
