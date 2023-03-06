import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import math

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class PlotGreek():

    def __init__(self, trial_obj, axis, file_names, path, name, offset_by_0_value=False):
        self.trial_obj = trial_obj
        self.axis = axis
        self.file_names = file_names
        self.path = path
        self.name = name
        self.offset_by_0_value = offset_by_0_value
    
    def plot_greek(self):
        for file_name in self.file_names:
            file_contents = self.get_file_contents(file_name)
            self.plot_file_contents(file_contents, file_name)

    def get_file_contents(self, file_name):
        file_path = os.path.join(self.path, file_name)
        with open(file_path, "r") as file:
            file.readline()
            file_contents = file.readlines()
        return file_contents

    def plot_file_contents(self, file_contents, file_name):
        self.set_detuning_and_greek(file_contents)
        if self.detuning is not None:
            self.label = file_name[:-4]
            self.make_plot_of_greek()
        
    def set_detuning_and_greek(self, file_contents):
        if len(file_contents) != 0:
            self.set_detuning_and_greek_from_file(file_contents)
        else:
            print("Warning: no data could be extracted from file in PlotGammaAndOmega")
            self.detuning, self.drift, self.greek = None, None, None

    def set_detuning_and_greek_from_file(self, file_contents):
        file_lines_decomposed = [[float(number) for number in line.strip().split('\t')]
                                 for line in file_contents]
        if len(file_lines_decomposed[0]) == 3:
            self.detuning, self.drift, self.greek = zip(*file_lines_decomposed)
            self.deviations = None
        else:
            self.detuning, self.drift, self.greek, self.deviations = zip(*file_lines_decomposed)
        self.process_file_output()

    def process_file_output(self):
        self.process_greek()
        acceptable_indices = self.get_acceptable_indices(self.greek)
        self.detuning = np.array(self.detuning)[acceptable_indices]
        self.drift = np.array(self.drift)[acceptable_indices]
        self.greek = np.array(self.greek)[acceptable_indices]
        self.filter_deviations(acceptable_indices)

    def process_greek(self):
        self.greek = np.abs(self.greek)
        if self.offset_by_0_value:
            self.offset_greek_by_0_value()

    def offset_greek_by_0_value(self):
        detuning_0_index = self.get_detuning_0_index()
        self.greek_0_value = self.greek[detuning_0_index]
        self.greek -= self.greek_0_value

    def get_detuning_0_index(self):
        if 0.0 in self.detuning:
            detuning_0_index = self.detuning.index(0.0)
        else:
            print(f"Warning: trial does not have data for 0 detuning\n{self.trial_obj}")
            detuning_0_index = 0
        return detuning_0_index

    def get_acceptable_indices(self, data):
        if len(data) > 2:
            acceptable_indices = self.get_acceptable_indices_median(data)
        else:
            acceptable_indices = np.arange(len(data))
        return acceptable_indices

    def get_acceptable_indices_median(self, data):
        deviations = np.abs(data - np.median(data))
        modified_deviation = np.average(deviations**(1/4))**4
        acceptable_indices = np.abs(deviations) < 4 * modified_deviation
        return acceptable_indices

    def filter_deviations(self, acceptable_indices):
        if self.deviations is not None:
            self.deviations = np.array(self.deviations)[acceptable_indices]

    def make_plot_of_greek(self):
        x_values = self.detuning - self.drift
        if hasattr(self, 'deviations') is False:
            self.axis.plot(x_values, self.greek, '.-', label=self.label)
        else:
            self.axis.errorbar(x_values, self.greek, fmt='.-', yerr=self.deviations, label=self.label)

    def add_plot_labels(self):
        self.add_axis_labels()
        self.axis.legend(bbox_to_anchor=(1.05, 1), loc = 2)
        self.axis.set_title(f"Sideband {self.name} vs Frequency")

    def add_axis_labels(self):
        self.add_x_axis_labels()
        self.add_y_axis_labels()

    def add_x_axis_labels(self):
        self.remove_edge_x_ticks()
        prefix, prefix_power = self.get_prefix_data()
        x_ticks = self.axis.get_xticks()
        x_labels = [f'{value:.0f}' for value in x_ticks/1000**prefix_power]
        self.axis.set_xticks(x_ticks, x_labels)
        self.axis.set_xlabel(r"Detuning $\left(\Delta = \frac{\omega_d - \omega_0}{2\pi}\right)$ "+ f"({prefix})")

    def remove_edge_x_ticks(self):
        x_ticks, x_labels = self.axis.get_xticks(), self.axis.get_xticklabels()
        x_ticks = x_ticks[1:-1]
        x_labels = x_labels[1:-1]
        self.axis.set_xticks(x_ticks, x_labels)

    def get_prefix_data(self):
        x_ticks = self.axis.get_xticks()
        max_x_tick = max(abs(x_ticks))
        prefix_power = math.floor(math.log(max_x_tick, 1000))
        prefix = {-1: "mHz", 0: "Hz", 1: "kHz", 2: "MHz", 3: "GHz", 4: "THz"}[prefix_power]
        return prefix, prefix_power

    def add_y_axis_labels(self):
        self.reset_y_ticks_and_labels()
        self.axis.set_ylabel(f"{self.name} (Hz)")

    def reset_y_ticks_and_labels(self):
        # This code appears unnecessary but ticks can go missing if it is not included
        y_ticks = self.axis.get_yticks()
        y_labels = self.axis.get_yticklabels()
        self.axis.set_yticks(y_ticks, y_labels)
