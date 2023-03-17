import os

import numpy as np

from Transmission import Transmission
from AlignedTransmission import AlignedTransmission
from Lines import Lines
from Line import Line
from Plots import Plots
from Utils import get_number_from_file_name
from Utils import convert_to_milliwatts
from Utils import get_group_size
from Utils import get_group_indexes

class Power():

    def __init__(self, sub_data_set, power, file_names):
        self.sub_data_set = sub_data_set
        self.process_power_input(power)
        self.file_names = file_names
        self.process_initial_input()
        self.create_transmission_objects()

    def process_power_input(self, power):
        self.power_string = str(power)
        self.power = convert_to_milliwatts(power)

    def process_initial_input(self):
        self.data_set = self.sub_data_set.data_set
        self.sort_file_names()
        self.paths = [os.path.join(self.sub_data_set.path, file_name)
                      for file_name in self.file_names]

    def sort_file_names(self):
        file_count_dict = {file_name: get_number_from_file_name("count", file_name, offset=0, number_type=int)
                           for file_name in self.file_names}
        if None not in file_count_dict.values():
            self.file_names = sorted(self.file_names, key=lambda x: file_count_dict[x])
    
    def output_file_names(self):
        print(f"\nOutputting {len(self.file_names)} file names for {self}")
        for file_name in self.file_names:
            print(file_name)

    def create_transmission_objects(self):
        self.transmission_objects = [Transmission(self, file_name, path)
                                     for file_name, path in zip(self.file_names, self.paths)]
        self.transmission_objects = np.array(self.transmission_objects)

    def read_raw_transmission(self):
        for transmission_obj in self.transmission_objects:
            transmission_obj.read_raw_transmission()

    def plot_transmission(self, option, group_size, subplots):
        plot_transmission_options = {"Raw": self.plot_transmission_raw,
                                     "Aligned": self.plot_transmission_aligned}
        plot_transmission_options[option](group_size, subplots)

    def plot_transmission_raw(self, group_size, subplots):
        transmission_raw_plots = self.get_transmission_raw_plots(group_size)
        title = f"{self} Transmission"
        self.create_plots(transmission_raw_plots, subplots, title)

    def get_transmission_raw_plots(self, group_size):
        transmission_objects_groups = self.get_transmission_objects_groups(group_size)
        transmission_raw_plots = [self.get_transmission_raw_lines(transmission_objects_group, index)
                                  for index, transmission_objects_group in enumerate(transmission_objects_groups)]
        return transmission_raw_plots

    def get_transmission_objects_groups(self, group_size):
        group_size = get_group_size(group_size, self.transmission_objects)
        group_indexes = get_group_indexes(len(self.transmission_objects), group_size)
        transmission_objects_groups = [self.transmission_objects[indexes] for indexes in group_indexes]
        return transmission_objects_groups

    def get_transmission_raw_lines(self, transmission_objects_group, index):
        lines_obj = self.create_lines_raw_obj(transmission_objects_group)
        lines_obj = self.set_lines_labels_raw(lines_obj, index)
        return lines_obj

    def create_lines_raw_obj(self, transmission_objects_group):
        line_objects = self.get_line_objects_raw(transmission_objects_group)
        lines_obj = Lines(line_objects)
        return lines_obj

    def get_line_objects_raw(self, transmission_objects_group):
        line_objects = [self.get_line_object_raw(transmission_obj)
                        for transmission_obj in transmission_objects_group]
        return line_objects

    def get_line_object_raw(self, transmission_obj):
        x_values = transmission_obj.frequency
        y_values = transmission_obj.S21
        line_obj = Line(x_values, y_values)
        return line_obj

    def set_lines_labels_raw(self, lines_obj, index):
        lines_obj.title = f"Group {index}"
        lines_obj.x_label = "Frequency (Hz)"
        lines_obj.y_label = "S21 (mW)"
        return lines_obj

    def plot_transmission_aligned(self, group_size, subplots):
        transmission_aligned_plots = [self.get_transmission_aligned_lines(transmission_aligned_obj, index)
                                      for index, transmission_aligned_obj in enumerate(self.transmission_aligned_objects)]
        title = f"{self} Transmission Aligned"
        self.create_plots(transmission_aligned_plots, subplots, title)

    def get_transmission_aligned_lines(self, transmission_aligned_obj, index):
        lines_obj = self.create_aligned_lines_obj(transmission_aligned_obj)
        lines_obj = self.set_lines_labels_aligned(lines_obj, transmission_aligned_obj, index)
        return lines_obj

    def create_aligned_lines_obj(self, transmission_aligned_obj):
        frequency = transmission_aligned_obj.frequency
        line_objects = [self.get_line_obj_aligned(transmission_obj, frequency)
                        for transmission_obj in transmission_aligned_obj.transmission_objects]
        lines_obj = Lines(line_objects)
        return lines_obj

    def set_lines_labels_aligned(self, lines_obj, transmission_aligned_obj, index):
        lines_obj.title = f"Group {index}"
        lines_obj.x_label = "Frequency (Hz)"
        lines_obj.y_label = "S21 (mW)"
        return lines_obj

    def get_line_obj_aligned(self, transmission_obj, frequency):
        x_values = frequency
        y_values = transmission_obj.S21_offset
        line_obj = Line(x_values, y_values)
        return line_obj
    
    def create_plots(self, lines_objects, subplots, title):
        plot_obj = Plots(lines_objects, subplots)
        plot_obj.title = title
        plot_obj.plot()

    def align_transmission(self, group_size):
        self.set_transmission_peaks()
        group_size = get_group_size(group_size, self.transmission_objects)
        group_indexes = get_group_indexes(len(self.transmission_objects), group_size)
        self.set_transmission_aligned_objects(group_indexes)

    def set_transmission_peaks(self):
        for transmission_obj in self.transmission_objects:
            transmission_obj.set_peak()

    def set_transmission_aligned_objects(self, group_indexes):
        self.transmission_aligned_objects = [self.get_transmission_aligned(indexes)
                                             for indexes in group_indexes]

    def get_transmission_aligned(self, indexes):
        transmission_objects = self.transmission_objects[indexes]
        transmission_aligned = AlignedTransmission(transmission_objects)
        transmission_aligned.align_transmissions()
        return transmission_aligned

    def __str__(self):
        string = (f"{self.sub_data_set}, {self.power_string} dBm")
        return string
