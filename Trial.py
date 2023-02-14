from Detuning import Detuning
import os
import matplotlib.pyplot as plt

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
        self.detuning_objects = sorted(self.detuning_objects,
                                       key = lambda detuning_obj: detuning_obj.detuning)

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
            raise Exception(f"Could not find {number_name} in file name:\n{file_name}")

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

    def process_S21(self):
        for detuning_obj in self.detuning_objects:
            detuning_obj.process_S21()

    def process_transmission(self):
        for detuning_obj in self.detuning_objects:
            detuning_obj.process_transmission()
    
    def process_omega(self):
        for detuning_obj in self.detuning_objects:
            detuning_obj.set_omega()

    def save_omega(self):
        omega_file_path = self.get_omega_file_path()
        with open(omega_file_path, "w") as file:
            for detuning_obj in self.detuning_objects:
                if hasattr(detuning_obj, "omega"):
                    file.writelines(f"{detuning_obj.detuning}\t{detuning_obj.omega}\n")

    def get_omega_file_path(self):
        parent_path = self.power_obj.data_set.omega_path
        data_set = self.power_obj.data_set.folder_name
        omega_file_name = f"{data_set}_{self.power_obj.folder_name}_{self.trial_number}.txt"
        omega_file_path = os.path.join(parent_path, omega_file_name)
        return omega_file_path
            
    def process_gamma(self):
        for detuning_obj in self.detuning_objects:
            detuning_obj.set_gamma()

    def save_gamma(self):
        gamma_file_path = self.get_gamma_file_path()
        with open(gamma_file_path, "w") as file:
            for detuning_obj in self.detuning_objects:
                file.writelines(f"{detuning_obj.detuning}\t{detuning_obj.gamma}\n")

    def get_gamma_file_path(self):
        parent_path = self.power_obj.data_set.gamma_path
        data_set = self.power_obj.data_set.folder_name
        gamma_file_name = f"{data_set}_{self.power_obj.folder_name}_{self.trial_number}.txt"
        gamma_file_path = os.path.join(parent_path, gamma_file_name)
        return gamma_file_path

    def create_trial_plots(self, plot_name):
        {"Detuning vs time": self.plot_detuning_vs_time,
         "Frequency of peak": self.plot_frequency_of_peak,
         "Transmission peak": self.plot_transmission_peak,
         "Colour plots": self.plot_colour_plots}[plot_name]()

    def plot_detuning_vs_time(self):
        detunings, timestamps = self.get_detunings_and_timestamps()
        plt.plot(timestamps, detunings)
        self.add_detuning_vs_time_labels()
        plt.show()

    def get_detunings_and_timestamps(self):
        detuning_time_data = [(detuning_obj.detuning, detuning_obj.timestamp)
                              for detuning_obj in self.detuning_objects]
        detunings, timestamps = zip(*detuning_time_data)
        return detunings, timestamps

    def add_detuning_vs_time_labels(self):
        plt.xlabel("Timestamp (s)")
        plt.ylabel("Detuning (Hz)")
        plt.title(f"Detuning vs Time for {self.power_obj.folder_name}")

    def plot_frequency_of_peak(self):
        peak_frequencies = [spectrum_obj.S21_centre_frequency
                            for detuning_obj in self.detuning_objects
                            for spectrum_obj in detuning_obj.spectrum_objects]
        plt.plot(peak_frequencies)
        self.add_frequency_of_peak_labels()
        plt.show()

    def add_frequency_of_peak_labels(self):
        plt.xlabel("Spectrum number")
        plt.ylabel("Frequency (Hz)")
        plt.title((f"Peak Frequency vs Spectrum Number\n"
                   f"for {self.power_obj.folder_name}"))

    def plot_transmission_peak(self):
        timestamps, transmission_peaks = self.get_transmission_peaks()
        plt.plot(timestamps, transmission_peaks, '.-')
        self.add_transmission_peak_labels()
        plt.show()

    def get_transmission_peaks(self):
        transmission_data = [(detuning_obj.timestamp,
                              detuning_obj.transmission.S21_centre_frequency)
                             for detuning_obj in self.detuning_objects]
        timestamps, transmission_peaks = zip(*transmission_data)
        return timestamps, transmission_peaks

    def add_transmission_peak_labels(self):
        plt.xlabel("Timestamp (s)")
        plt.ylabel("Frequency (Hz)")
        plt.title((f"Peak Frequency of Transmission\n"
                   f"vs Time for {self.power_obj.folder_name}, Trial {self.trial_number}"))

    def plot_colour_plots(self):
        for i in self.detuning_objects:
            print(len(i.S21), len(i.frequency))

    def create_detuning_plots(self, plot_name):
        for detuning_obj in self.detuning_objects:
            detuning_obj.create_detuning_plots(plot_name)

    def output_detunings(self):
        for detuning_obj in self.detuning_objects:
            print(detuning_obj)

    def output_gammas(self):
        for detuning_obj in self.detuning_objects:
            print("Outputting gamma")
            print(detuning_obj.gamma)
            print(detuning_obj)

    def __str__(self):
        string = (f"Power: {self.power_obj.power_string}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum path: {self.spectrum_path}\n"
                  f"Trial number: {self.trial_number}\n")
        return string
