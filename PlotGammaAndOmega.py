import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import math

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class PlotGreek():

    def __init__(self, trial_obj, axis):
        self.trial_obj = trial_obj
        self.axis = axis
    
    def generate_plot(self, variable_name, parent_path, format_type):
        fig, ax = plt.subplots()
        ax = self.plot_detuning_vs_greek(parent_path, ax)
        self.add_plot_labels(variable_name)
        plot_path = os.path.join(parent_path, f"{variable_name} Plot")
        plt.savefig(plot_path, bbox_inches='tight', format = format_type)
        return self.ax

    def plot_detuning_vs_greek(self, path):
        for file_name in sorted(os.listdir(path)):
            if file_name.endswith(".txt") and not file_name.endswith("All.txt"):
                file_contents = self.get_file_contents(path, file_name)
                label = file_name[:-4]
                detuning, drift, greek = self.get_detuning_and_greek(file_contents)
                if detuning is not None:
                    ax.plot(detuning - drift, greek, '.-', label = label)

    def get_underscore_locations(self, file):
        underscore_locations = [index for index, character in enumerate(file)
                                if character == "_"]
        return underscore_locations

    def get_file_contents(self, path, file_name):
        file_path = os.path.join(path, file_name)
        with open(file_path, "r") as file:
            file.readline()
            file_contents = file.readlines()
        return file_contents

    def get_detuning_and_greek(self, file_contents):
        if len(file_contents) != 0:
            detuning, drift, greek = self.get_detuning_and_greek_from_file(file_contents)
        else:
            print("Warning: no data could be extracted from file")
            detuning, drift, greek = None, None, None
        return detuning, drift, greek

    def get_detuning_and_greek_from_file(self, file_contents):
        file_lines_decomposed = [[float(number) for number in line.strip().split('\t')]
                                 for line in file_contents]
        detuning, drift, greek = zip(*file_lines_decomposed)
        greek = np.abs(greek)
        acceptable_indices = self.get_acceptable_indices(greek)
        detuning = np.array(detuning)[acceptable_indices]
        drift = np.array(drift)[acceptable_indices]
        greek = np.array(greek)[acceptable_indices]
        return detuning, drift, greek

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

    def output_outliers(self, file_lines_decomposed, file_name):
        for line in file_lines_decomposed:
            if abs(line[1]) >= 200:
                print((f"Detuning: {line[0]}\n"
                       f"Value: {line[1]}\n"
                       f"File name: {file_name}\n"))

    def add_plot_labels(self, variable_name):
        self.add_axis_labels(variable_name)
        self.axis.legend(bbox_to_anchor=(1.05, 1), loc = 2)
        self.axis.set_title(f"Sideband {variable_name} vs Frequency")

    def add_axis_labels(self, variable_name):
        self.plot_labels_x_axis()
        self.axis.set_ylabel(f"{variable_name} (Hz)")

    def plot_labels_x_axis(self):
        self.set_x_ticks()
        prefix, prefix_power = self.get_prefix_data()
        x_ticks = self.axis.get_xticks()
        x_labels = [f'{value:.0f}' for value in x_ticks/1000**prefix_power]
        self.axis.set_xticks(x_ticks, x_labels)
        self.axis.set_xlabel(f"Frequency ({prefix})")

    def set_x_ticks(self):
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

    def plot_greek(self, file_path):
        for file_name in sorted(os.listdir(file_path)):
            if file_name.endswith(".txt") and not file_name.endswith("All.txt"):
                file_contents = self.get_file_contents(file_path, file_name)
                self.plot_file_contents(file_contents, file_name)

    def plot_file_contents(self, file_contents, file_name):
        label = file_name[:-4]
        detuning, drift, greek = self.get_detuning_and_greek(file_contents)
        if detuning is not None:
            self.axis.plot(detuning - drift, greek, '.-', label = label)
