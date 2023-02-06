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
        self.set_detuning_objects()

    def set_parent_information(self, power_obj):
        self.power_obj = power_obj
        self.power = power_obj.power
        self.data_set = power_obj.data_set

    def set_trial_number(self):
        underscore_locations = self.get_underscore_locations(self.transmission_path, 0)
        trial_number_starting_index = underscore_locations[-1] + 1
        self.trial_number = self.transmission_path[trial_number_starting_index:]
            
    def get_underscore_locations(self, file_name, limit=0):
        underscore_locations = [index for index, character in enumerate(file_name)
                                if character == "_" and index >= limit]
        return underscore_locations

    def get_timestamp_from_file_name(self, file_name):
        timestamp = self.get_number_from_file_name(file_name, "timestamp")
        return timestamp

    def set_detuning_objects(self):
        set_detuning_objects_functions = {1: self.set_detuning_objects_a,
                                          2: self.set_detuning_objects_b,
                                          3: self.set_detuning_objects_b}
        set_detuning_objects_functions[self.data_set.folder_structure_type]()

    def set_detuning_objects_a(self):
        self.detuning_objects = [self.get_detuning_object_a(file_name)
                                 for file_name in os.listdir(self.spectrum_path)]
        for detuning in self.detuning_objects:
            print(detuning)

    def get_detuning_object_a(self, file_name):
        detuning = self.get_number_from_file_name(file_name, "detuning")
        timestamp = self.get_number_from_file_name(file_name, "timestamp")
        spectrum_file_paths = [os.path.join(self.spectrum_path, file_name)]
        transmission_file_path = self.get_transmission_file_path(timestamp)
        detuning = Detuning(self, detuning, timestamp, transmission_file_path, spectrum_file_paths)
        return detuning

    def get_transmission_file_path(self, timestamp):
        for file_name in os.listdir(self.transmission_path):
            candidate_timestamp = self.get_number_from_file_name(file_name, "timestamp")
            if timestamp == candidate_timestamp:
                transmission_file_path = os.path.join(self.transmission_path, file_name)
                return transmission_file_path
        raise Exception(f"Could not find corresponding transmission for timestamp {timestamp}")

    def set_detuning_objects_b(self):
        pass

    def get_number_from_file_name(self, file_name, number_name):
        underscore_locations = self.get_underscore_locations(file_name, len(number_name))
        left_index = self.get_number_left_index(underscore_locations, file_name, number_name)
        right_index = self.get_number_right_index(left_index, file_name)
        number = self.get_number(file_name, left_index, right_index)
        return number

    def get_number_left_index(self, underscore_locations, file_name, number_name):
        try:
            number_left_index = [index for index in underscore_locations
                                 if file_name[index - len(number_name):index] == number_name][0] + 1
            return number_left_index
        except:
            raise Exception(f"Could not find {number_name} in file name:\n{file_name}")

    def get_number_right_index(self, left_index, file_name):
        right_index = left_index
        decimal_characters = "0123456789.-"
        while file_name[right_index] in decimal_characters:
            right_index += 1
        return right_index

    def get_number(self, file_name, left_index, right_index):
        try:
            number = float(file_name[left_index:right_index])
            return number
        except:
            raise Exception((f"Could not convert number to float\n"
                             f"File name: {file_name}\n"))

    def __str__(self):
        string = (f"Power: {self.power}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum path: {self.spectrum_path}\n"
                  f"Trial number: {self.trial_number}\n")
        return string
