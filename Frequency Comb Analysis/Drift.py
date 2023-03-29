import os

import numpy as np

from Detuning import Detuning
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

    def plot_spectra(self, subplots, detunings, groups, noise, markers, fit):
        self.plot_obj = DriftPlot(self, subplots)
        self.plot_obj.set_data_plotting_instructions(detunings, groups)
        self.plot_obj.set_peak_plotting_instructions(noise, markers, fit)
        self.plot_obj.plot_spectra()

    def plot_peak_fits(self, groups, legend):
        if hasattr(self, "drift_peak_fit"):
            self.drift_peak_fit.plot_peak_fits(groups, legend)
        else:
            raise AttributeError("Run 'load_peak_fits' method first")
    
    def __str__(self):
        string = f"{self.data_set}, Drift {self.drift_value} dBm"
        return string
