import os
from Detuning import Detuning

class Trial():

    """
    This class handles all the data for a trial done at a specific power.
    Organising the processing or detunings happens here.
    Folder structure "a" is where all the detunings for a trial are stored in one
    folder. Folder structure "b" is where each detuning has it's own folder.
    15112022 is type a, 16112022_overnight and 19112022 are type b.
    """
    
    def __init__(self, power_obj, transmission_path, spectrum_path):
        self.set_parent_information(power_obj)
        self.transmission_path = transmission_path
        self.spectrum_path = spectrum_path
        self.set_trial_number()
        self.set_files_list()
        self.set_detuning_paths()

    def set_parent_information(self, power_obj):
        self.power_obj = power_obj
        self.power = power_obj.power
        self.data_set = power_obj.data_set

    def set_trial_number(self):
        underscore_locations = [index
                                for index, character in enumerate(self.transmission_path)
                                if character == "_"]
        trial_number_starting_index = underscore_locations[-1] + 1
        self.trial_number = self.transmission_path[trial_number_starting_index:]

    def set_files_list(self):
        self.spectrum_file_names = sorted(os.listdir(self.spectrum_path), key=self.get_timestamp)

    def get_timestamp(self, file_name):
        underscore_locations = self.get_underscore_locations(file_name, 9)
        timestamp_location = self.get_timestamp_location(underscore_locations, file_name)
        left_index = underscore_locations[timestamp_location] + 1
        right_index = underscore_locations[timestamp_location + 1]
        timestamp = float(file_name[left_index:right_index])
        
    def get_underscore_locations(self, file_name, limit=0):
        underscore_locations = [index for index, character in enumerate(file_name)
                                if character == "_" and index >= limit]
        return underscore_locations

    def get_timestamp_location(self, underscore_locations, file_name):
        try:
            timestamp_location = [index for index, location in enumerate(underscore_locations)
                                  if file_name[location-9:location] == "timestamp"][0]
        except:
            raise Exception(f"Could not find 'timestamp' in file name:\n{file_name}")
        return timestamp_location

    def set_detuning_paths(self):
        set_detuning_paths_functions = {1: self.set_detuning_paths_a,
                                        2: self.set_detuning_paths_b,
                                        3: self.set_detuning_paths_b}
        set_detuning_paths_functions[self.data_set.folder_structure_type]()

    def set_detuning_paths_a(self):
        pass

    def set_detuning_paths_b(self):
        pass

    def __str__(self):
        string = (f"Power: {self.power}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum path: {self.spectrum_path}\n"
                  f"Trial number: {self.trial_number}\n")
        return string
