import os

import numpy as np

from Detuning import Detuning
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Plotting.PlotUtils import get_group_size
from Plotting.PlotUtils import get_group_indexes
from Utils import get_number_from_file_name
from Utils import get_number_from_string
from Utils import convert_to_milliwatts
from Utils import get_sliced_list

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

    def process_spectrum(self, detunings):
        detuning_objects = get_sliced_list(self.detuning_objects, detunings)
        for detuning_obj in detuning_objects:
            print(f"Processing spectrum for {detuning_obj}")
            detuning_obj.process_spectrum()

    def plot_spectra(self, subplots, detunings):
        detuning_objects = get_sliced_list(self.detuning_objects, detunings)
        detuning_lines_objects = self.get_detuning_lines_objects(detuning_objects)
        title = f"{self} Frequency Comb"
        self.create_plots(detuning_lines_objects, subplots, title)

    def get_detuning_lines_objects(self, detuning_objects_group):
        lines_objects = [self.get_detuning_lines_obj(detuning_obj)
                         for detuning_obj in detuning_objects_group]
        return lines_objects

    def get_detuning_lines_obj(self, detuning_obj):
        lines_obj = self.create_lines_obj(detuning_obj)
        self.set_lines_labels(lines_obj, detuning_obj)
        return lines_obj

    def create_lines_obj(self, detuning_obj):
        line_objects = self.get_line_objects(detuning_obj)
        lines_obj = Lines(line_objects)
        return lines_obj

    def get_line_objects(self, detuning_obj):
        line_objects = [self.get_line_object(group_obj)
                        for group_obj in detuning_obj.group_objects]
        return line_objects

    def get_line_object(self, group_obj):
        x_values = group_obj.frequency
        y_values = group_obj.S21
        line_obj = Line(x_values, y_values)
        return line_obj

    def set_lines_labels(self, lines_obj, detuning_obj):
        lines_obj.title = f"Detuning: {detuning_obj.detuning} Hz"
        lines_obj.x_label = "Frequency (Hz)"
        lines_obj.y_label = "S21 (dBm)"

    def create_plots(self, lines_objects, subplots, title):
        plot_obj = Plots(lines_objects, subplots, "semilogy")
        plot_obj.title = title
        plot_obj.plot()

    def set_peak_coordinates(self, detunings):
        detuning_objects = get_sliced_list(self.detuning_objects, detunings)
        for detuning_obj in detuning_objects:
            detuning_obj.set_peak_coordinates()

    def output_folder_groups(self):
        self.output_detuning_folders()
        self.output_transmission_files()
        self.output_probe_power()

    def output_detuning_folders(self):
        print(f"\nOutputting Detuning Folders for {self.drift_value} dBm")
        for folder_path in self.detuning_folders:
            print(os.path.basename(folder_path))

    def output_transmission_files(self):
        print(f"\nOutputting Transmission Files for {self.drift_value} dBm")
        for transmission_path in self.transmission_paths:
            print(os.path.basename(transmission_path))

    def output_probe_power(self):
        print((f"\nOutputting Probe Power File for {self.drift_value} dBm\n"
               f"{self.drift_probe_path}\n"
               f"{os.path.basename(self.drift_probe_path)}"))

    def __str__(self):
        string = f"{self.data_set}, Drift {self.drift_value} dBm"
        return string
