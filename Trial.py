import matplotlib.pyplot as plt
import os
from Detuning import Detuning
from Utils import get_file_contents

class Trial():

    """
    This class handles all the data for a trial done at a specific power.
    Organising the processing or detunings happens here.
    
    Folder structure "a" is where all the detunings for a trial are stored in one
    folder. Folder structure "b" is where each detuning has it's own folder.
    15112022 is type a, 16112022_overnight and 19112022 are type b.
    """
    
    def __init__(self, power_obj, trial_number, transmission_path, spectrum_path):
        self.set_parent_information(power_obj)
        self.transmission_path = transmission_path
        self.spectrum_path = spectrum_path
        self.trial_number = trial_number
        self.set_detuning_objects()

    def set_parent_information(self, power_obj):
        self.power_obj = power_obj
        self.power = power_obj.power
        self.data_set = power_obj.data_set

    def set_detuning_objects(self):
        set_detuning_objects_functions = {1: self.set_detuning_objects_a,
                                          2: self.set_detuning_objects_b,
                                          3: self.set_detuning_objects_b}
        set_detuning_objects_functions[self.data_set.folder_structure_type]()
        self.process_detuning_objects()
    
    def set_detuning_objects_a(self):
        spectrum_files = self.get_spectrum_files()
        self.detuning_objects = [self.get_detuning_object_a(detuning, spectrum_files)
                                 for detuning, spectrum_files in spectrum_files.items()]

    def get_spectrum_files(self):
        spectrum_files = self.initialise_spectrum_files()
        spectrum_files = self.populate_spectrum_files(spectrum_files)
        spectrum_files = self.sort_spectrum_files(spectrum_files)
        return spectrum_files

    def initialise_spectrum_files(self):
        spectrum_files = {self.get_number_from_file_name(file_name, "detuning"): []
                          for file_name in os.listdir(self.spectrum_path)}
        return spectrum_files

    def populate_spectrum_files(self, spectrum_files):
        for file_name in os.listdir(self.spectrum_path):
            detuning = self.get_number_from_file_name(file_name, "detuning")
            spectrum_files[detuning].append(file_name)
        return spectrum_files

    def sort_spectrum_files(self, spectrum_files):
        for detuning in spectrum_files.keys():
            spectrum_files[detuning] = sorted(spectrum_files[detuning],
                                              key=lambda x:x[-7:])
        return spectrum_files

    def get_detuning_object_a(self, detuning, spectrum_files):
        timestamp = self.get_number_from_file_name(spectrum_files[0], "timestamp")
        spectrum_file_paths = [os.path.join(self.spectrum_path, file_name)
                               for file_name in spectrum_files]
        transmission_file_path = self.get_transmission_file_path(timestamp)
        detuning_obj = Detuning(self, detuning, timestamp, transmission_file_path, spectrum_file_paths)
        return detuning_obj

    def get_transmission_file_path(self, timestamp):
        for file_name in os.listdir(self.transmission_path):
            candidate_timestamp = self.get_number_from_file_name(file_name, "timestamp")
            if timestamp == candidate_timestamp:
                transmission_file_path = os.path.join(self.transmission_path, file_name)
                return transmission_file_path
        raise Exception(f"Could not find corresponding transmission for timestamp {timestamp}")

    def set_detuning_objects_b(self):
        folder_names = sorted(os.listdir(self.spectrum_path))
        self.detuning_objects = [self.get_detuning_object_b(folder_name)
                                 for folder_name in folder_names
                                 if self.detuning_folder_non_empty(folder_name)]

    def get_detuning_object_b(self, folder_name):
        detuning, timestamp = self.get_detuning_and_timestamp_from_folder(folder_name)
        spectrum_file_paths = self.get_spectrum_file_paths(folder_name)
        transmission_file_path = self.get_transmission_file_path(timestamp)
        detuning = Detuning(self, detuning, timestamp, transmission_file_path, spectrum_file_paths)
        return detuning

    def process_detuning_objects(self):
        self.detuning_objects = sorted(self.detuning_objects,
                                       key = lambda detuning_obj: detuning_obj.detuning)

    def get_detuning_and_timestamp_from_folder(self, folder_name):
        folder_path = os.path.join(self.spectrum_path, folder_name)
        file_name = os.listdir(folder_path)[0]
        detuning = self.get_number_from_file_name(file_name, "detuning")
        timestamp = self.get_number_from_file_name(file_name, "timestamp")
        return detuning, timestamp

    def get_spectrum_file_paths(self, folder_name):
        folder_path = os.path.join(self.spectrum_path, folder_name)
        spectrum_file_names = list(os.listdir(folder_path))
        spectrum_file_names = sorted(spectrum_file_names, key = self.get_counter)
        spectrum_file_paths = [os.path.join(folder_path, file_name)
                               for file_name in spectrum_file_names]
        return spectrum_file_paths

    def detuning_folder_non_empty(self, folder_name):
        folder_path = os.path.join(self.spectrum_path, folder_name)
        if len(os.listdir(folder_path)) != 0:
            return True
        else:
            print(f"UNEXPECTED: Folder is empty: {folder_path}")
            return False

    def get_counter(self, file_name):
        counter = self.get_number_from_file_name(file_name, "counter")
        return counter
            
    def get_underscore_locations(self, file_name, limit=0):
        underscore_locations = [index for index, character in enumerate(file_name)
                                if character == "_" and index >= limit]
        return underscore_locations

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
            raise Exception(f"Could not find '{number_name}' in file name:\n{file_name}")

    def get_number_right_index(self, left_index, file_name):
        right_index = left_index
        while self.is_index_valid(right_index, file_name):
            right_index += 1
        return right_index

    def is_index_valid(self, index, file_name):
        is_number = (file_name[index] in "0123456789.-")
        is_not_at_end_of_file = (index < len(file_name) - 4)
        is_valid = is_number and is_not_at_end_of_file
        return is_valid

    def get_number(self, file_name, left_index, right_index):
        try:
            number = float(file_name[left_index:right_index])
            return number
        except:
            raise Exception((f"Could not convert number to float\n"
                             f"File name: {file_name}\n"
                             f"left_index: {left_index}, right index: {right_index}"
                             f"{file_name[left_index:right_index]}\n"))

    def process_spectrum(self):
        self.set_spectrum_file_path()
        with open(self.spectrum_file_path, "w+") as file:
            file.writelines(f"Detuning\tspectrum_peak_index\tspectrum_peak_frequency\tIndex\n")
            for detuning_obj in self.detuning_objects:
                file = self.write_spectrum_peaks_to_file(file, detuning_obj)

    def set_spectrum_file_path(self):
        spectrum_folder_path = self.data_set.spectrum_path
        file_name = f"{self.data_set.folder_name}_{self.power_obj.folder_name}_{self.trial_number}.txt"
        self.spectrum_file_path = os.path.join(spectrum_folder_path, file_name)

    def write_spectrum_peaks_to_file(self, file, detuning_obj):
        spectrum_peak_indexes, spectrum_peak_frequencies, file_indexes = detuning_obj.get_spectrum_peaks()
        for (peak_index, frequency, file_index) in zip(spectrum_peak_indexes, spectrum_peak_frequencies, file_indexes):
            file.writelines(f"{detuning_obj.detuning}\t{peak_index}\t{frequency}\t{file_index}\n")
        return file

    def set_spectrum(self):
        self.set_spectrum_file_path()
        if os.path.exists(self.spectrum_file_path) == False:
            raise Exception((f"Spectrum data could not be found for {self.trial_number}\n"
                             f"Run process_spectrum method first"))
        else:
            self.extract_spectrum_from_file()

    def extract_spectrum_from_file(self):
        spectrum_file_contents = self.get_file_contents(self.spectrum_file_path)
        for detuning_obj in self.detuning_objects:
            detuning_obj.extract_spectrum_from_file_detuning(spectrum_file_contents)

    def process_transmission(self):
        self.set_transmission_file_path()
        with open(self.transmission_file_path, "w+") as file:
            file.writelines(f"Detuning (Hz)\tTransmission peak index\tTransmission peak frequency (Hz)\tCavity frequency (Hz)\n")
            for detuning_obj in self.detuning_objects:
                file = self.write_transmission_data_to_file(file, detuning_obj)

    def set_transmission_file_path(self):
        transmission_folder_path = self.data_set.transmission_path
        file_name = f"{self.data_set.folder_name}_{self.power_obj.folder_name}_{self.trial_number}.txt"
        self.transmission_file_path = os.path.join(transmission_folder_path, file_name)

    def write_transmission_data_to_file(self, file, detuning_obj):
        peak_index, peak_frequency = detuning_obj.get_transmission_peak()
        if peak_index is not None:
            cavity_frequency = detuning_obj.cavity_frequency
            file.writelines(f"{detuning_obj.detuning}\t{peak_index}\t{peak_frequency}\t{cavity_frequency}\n")
        return file

    def set_transmission(self):
        self.set_transmission_file_path()
        if os.path.exists(self.transmission_file_path) == False:
            raise Exception((f"Transmission data could not be found for {self.trial_number}\n"
                             f"Run process_transmission method first"))
        else:
            self.do_set_transmission()

    def do_set_transmission(self):
        self.extract_transmission_from_file()
        self.set_next_detuning_objects()

    def extract_transmission_from_file(self):
        transmission_file_contents = self.get_file_contents(self.transmission_file_path)
        detunings, indexes, frequencies, cavity_frequencies = zip(*transmission_file_contents)
        for detuning_obj in self.detuning_objects:
            self.extract_transmission_from_file_detuning(detunings, detuning_obj, transmission_file_contents)

    def extract_transmission_from_file_detuning(self, detunings, detuning_obj, transmission_file_contents):
        if detuning_obj.detuning in detunings:
            self.do_extract_transmission_from_file_detuning(detunings, detuning_obj, transmission_file_contents)
        else:
            detuning_obj.valid = False

    def do_extract_transmission_from_file_detuning(self, detunings, detuning_obj, transmission_file_contents):
        detuning_index = detunings.index(detuning_obj.detuning)
        _, index, frequency, cavity_frequency = transmission_file_contents[detuning_index]
        detuning_obj.extract_transmission_from_file_detuning(index, frequency, cavity_frequency)

    def get_data_files(self, folder_path):
        all_file_names = sorted(os.listdir(folder_path))
        data_files = [file_name
                      for file_name in all_file_names
                      if self.is_valid_file_name(file_name)]
        return data_files

    def is_valid_file_name(self, file_name):
        if file_name.endswith(".txt") and not file_name.endswith("All.txt"):
            power = self.get_number_from_file_name(file_name, "Power")
            trial = self.get_number_from_file_name(file_name, "Trial")
            if power == float(self.power_obj.power_string):
                if trial == float(self.trial_number):
                    return True
        return False
    
    def set_next_detuning_objects(self):
        for index in range(len(self.detuning_objects) - 1):
            if self.detuning_objects[index].valid:
                self.set_next_detuning_object_valid(index)
        self.detuning_objects[-1].next_detuning = self.detuning_objects[-1]

    def set_next_detuning_object_valid(self, index):
        if self.detuning_objects[index + 1].valid:
            self.detuning_objects[index].next_detuning = self.detuning_objects[index + 1]
        else:
            self.detuning_objects[index].next_detuning = self.detuning_objects[index]

    def output_detunings(self):
        for detuning_obj in self.detuning_objects:
            print(detuning_obj)

    def __str__(self):
        string = (f"Power: {self.power_obj.power_string}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum path: {self.spectrum_path}\n"
                  f"Trial number: {self.trial_number}\n")
        return string
