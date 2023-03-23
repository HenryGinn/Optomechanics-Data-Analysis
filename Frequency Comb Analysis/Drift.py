import os

import numpy as np

from Detuning import Detuning
from DriftPlot import DriftPlot
from Utils import get_number_from_file_name
from Utils import get_number_from_string
from Utils import convert_to_milliwatts
from Utils import get_sliced_list
from Utils import make_folder

class Drift():

    def __init__(self, data_set, folder_name):
        self.data_set = data_set
        self.set_path_data(folder_name)
        self.set_drift(folder_name)
        self.process_folder()

    def set_path_data(self, folder_name):
        self.folder_name = folder_name
        self.path = os.path.join(self.data_set.path, folder_name)

    def set_drift(self, folder_name):
        self.drift_value = get_number_from_file_name("Drift", folder_name)
        self.drift = convert_to_milliwatts(self.drift_value)

    def process_folder(self):
        self.set_folder_groups()
        self.process_detuning_folders()
        self.process_transmission_paths()
        self.create_spectrum_objecs()

    def set_folder_groups(self):
        self.initialise_folder_groups()
        for file_name in os.listdir(self.path):
            path = os.path.join(self.path, file_name)
            self.set_folder_groups_path(path)

    def initialise_folder_groups(self):
        self.detuning_folders = []
        self.transmission_paths = []

    def set_folder_groups_path(self, path):
        if os.path.isdir(path):
            self.detuning_folders.append(path)
        else:
            self.set_folder_groups_file(path)

    def set_folder_groups_file(self, path):
        if os.path.basename(path).startswith("Drift"):
            self.drift_probe_path = path
        else:
            self.transmission_paths.append(path)

    def process_detuning_folders(self):
        detuning_dict = {path: self.get_detuning_from_path(path)
                         for path in self.detuning_folders}
        self.detunings = sorted(list(set(list(detuning_dict.values()))))
        self.set_detuning_paths_dict(detuning_dict)
        self.set_detuning_objects()
        
    def get_detuning_from_path(self, path):
        folder_name = os.path.basename(path)
        separator_index = folder_name.index(".")
        detuning_value = folder_name[:separator_index]
        detuning_value = get_number_from_string(detuning_value, int)
        return detuning_value

    def set_detuning_paths_dict(self, detuning_dict):
        self.detuning_paths_dict = {detuning: [] for detuning in self.detunings}
        for path, detuning in detuning_dict.items():
            self.detuning_paths_dict[detuning].append(path)

    def set_detuning_objects(self):
        self.detuning_objects = [Detuning(self, detuning, paths)
                                 for detuning, paths in self.detuning_paths_dict.items()]
        self.detuning_objects = get_sliced_list(self.detuning_objects, self.data_set.detuning_indexes)
        self.detuning_objects = np.array(self.detuning_objects)

    def process_transmission_paths(self):
        transmission_timestamps = self.get_transmission_timestamps()
        for detuning_obj in self.detuning_objects:
            for group_obj in detuning_obj.group_objects:
                group_obj.transmission_path = transmission_timestamps[group_obj.timestamp]

    def get_transmission_timestamps(self):
        transmission_timestamps = {self.get_transmission_timestamp(transmission_path): transmission_path
                                   for transmission_path in self.transmission_paths}
        return transmission_timestamps

    def get_transmission_timestamp(self, transmission_path):
        file_name = os.path.basename(transmission_path)
        timestamp = get_number_from_file_name("timestamp", file_name)
        return timestamp

    def create_spectrum_objecs(self):
        for detuning_obj in self.detuning_objects:
            for group_obj in detuning_obj.group_objects:
                group_obj.create_spectrum_objects()

    def create_aligned_spectra_folder(self):
        self.aligned_spectra_path = os.path.join(self.data_set.aligned_spectra_path,
                                                 self.folder_name)
        make_folder(self.aligned_spectra_path)

    def populate_aligned_spectra_folder(self):
        for detuning_obj in self.detuning_objects:
            detuning_obj.create_aligned_spectra_folder()
            detuning_obj.set_aligned_spectra_paths()

    def set_aligned_spectra(self, detunings):
        detuning_objects = get_sliced_list(self.detuning_objects, detunings)
        print(f"Processing spectrum for {self}")
        for detuning_obj in detuning_objects:
            detuning_obj.set_aligned_spectra()

    def load_aligned_spectra(self):
        for detuning_obj in self.detuning_objects:
            detuning_obj.load_aligned_spectra()

    def set_noise_threshold_paths(self):
        self.create_noise_threshold_folder()
        for detuning_obj in self.detuning_objects:
            detuning_obj.set_noise_threshold_paths()

    def create_noise_threshold_folder(self):
        self.noise_threshold_path = os.path.join(self.data_set.noise_threshold_path,
                                             f"{self.drift_value} dBm")
        make_folder(self.noise_threshold_path)

    def save_noise_threshold(self):
        print(f"Finding noise floor for {self}")
        for detuning_obj in self.detuning_objects:
            detuning_obj.save_noise_threshold()

    def load_noise_threshold(self):
        for detuning_obj in self.detuning_objects:
            detuning_obj.load_noise_threshold()

    def set_peak_coordinates_paths(self):
        self.create_peak_coordinates_folder()
        for detuning_obj in self.detuning_objects:
            detuning_obj.set_peak_coordinates_paths()

    def create_peak_coordinates_folder(self):
        self.peak_coordinates_path = os.path.join(self.data_set.peak_coordinates_path,
                                                  f"{self.drift_value} dBm")
        make_folder(self.peak_coordinates_path)

    def set_peak_coordinates(self, detunings):
        detuning_objects = get_sliced_list(self.detuning_objects, detunings)
        for detuning_obj in detuning_objects:
            detuning_obj.set_peak_coordinates()

    def load_peak_coordinates(self):
        for detuning_obj in self.detuning_objects:
            detuning_obj.load_peak_coordinates()

    def save_fit_peaks(self):
        for detuning_obj in self.detuning_objects:
            detuning_obj.fit_peaks()
        self.save_peak_lines()

    def save_peak_lines(self):
        peak_lines_path = os.path.join(self.data_set.peak_fitting_path,
                                       f"{self.drift_value} dBm")
        with open(peak_lines_path, "w") as file:
            self.save_peak_lines_to_file(file)

    def save_peak_lines_to_file(self, file):
        file.writelines(("Detuning (Hz)\tGroup\tLeft Gradient\tLeft Intercept"
                         "\tRight Gradient\tRight Intercept\n"))
        for detuning_obj in self.detuning_objects:
            detuning_obj.save_peak_lines_to_file(file)

    def plot_spectra(self, subplots, detunings, groups, noise, markers, fit):
        self.plot_obj = DriftPlot(self, subplots)
        self.plot_obj.set_data_plotting_instructions(detunings, groups)
        self.plot_obj.set_peak_plotting_instructions(noise, markers, fit)
        self.plot_obj.plot_spectra()
    
    def __str__(self):
        string = f"{self.data_set}, Drift {self.drift_value} dBm"
        return string
