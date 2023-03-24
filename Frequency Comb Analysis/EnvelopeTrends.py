import os

import numpy as np

from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import process_line

class EnvelopeTrends():

    def __init__(self, data_set_obj):
        self.data_set_obj = data_set_obj
        self.set_functions()
        self.loaded = False

    def set_functions(self):
        self.functions = {"Save": self.save_envelope_data,
                          "Load": self.load_envelope_data,
                          "Plot": self.create_plot}

    def execute(self, command, *args):
        function = self.functions[command]
        function(*args)

    def save_envelope_data(self):
        self.set_paths()
        with open(self.path, "w") as file:
            file.writelines("Drift (dBm)\tDetuning (Hz)\tGradient Average\tGradient Standard Deviation\tIntercept\tIntercept Standard Deviation\n")
            self.write_envelope_data_to_file(file)

    def write_envelope_data_to_file(self, file):
        for drift_obj in self.data_set_obj.drift_objects:
            for detuning_obj in drift_obj.detuning_objects:
                self.write_detuning_envelope_data_to_file(file, detuning_obj)

    def write_detuning_envelope_data_to_file(self, file, detuning_obj):
        self.write_drift_and_detuning(file, detuning_obj)
        self.write_detuning_gradient_data(file, detuning_obj)
        self.write_detuning_intercept_data(file, detuning_obj)

    def write_drift_and_detuning(self, file, detuning_obj):
        drift = detuning_obj.drift_obj.drift_value
        detuning = detuning_obj.detuning
        file.writelines(f"{drift}\t{detuning}\t")

    def write_detuning_gradient_data(self, file, detuning_obj):
        gradients = np.array([group_objects.peaks_fit_obj.fitting_parameters[0]
                              for group_objects in detuning_obj.group_objects])
        gradient_mean = np.mean(gradients)
        gradient_standard_deviation = np.std(gradients)
        file.writelines(f"{gradient_mean}\t{gradient_standard_deviation}\t")

    def write_detuning_intercept_data(self, file, detuning_obj):
        intercepts = np.array([group_objects.peaks_fit_obj.fitting_parameters[1]
                               for group_objects in detuning_obj.group_objects])
        intercept_mean = np.mean(intercepts)
        intercept_standard_deviation = np.std(intercepts)
        file.writelines(f"{intercept_mean}\t{intercept_standard_deviation}\n")

    def load_envelope_data(self):
        self.ensure_envelope_data_file_exists()
        with open(self.path, "r") as file:
            file.readline()
            self.load_envelope_data_from_file(file)
        self.loaded = True

    def ensure_envelope_data_file_exists(self):
        self.set_paths()
        if not os.path.exists(self.path):
            self.execute("Save")

    def load_envelope_data_from_file(self, file):
        for drift_obj in self.data_set_obj.drift_objects:
            for detuning_obj in drift_obj.detuning_objects:
                self.load_envelope_data_to_detuning_obj(detuning_obj, file)

    def load_envelope_data_to_detuning_obj(self, detuning_obj, file):
        line = file.readline()
        line = process_line(line, file)
        (_, _, detuning_obj.gradient_mean, detuning_obj.gradient_deviation,
         detuning_obj.intercept_mean, detuning_obj.intercept_deviation) = line

    def set_paths(self):
        self.set_folder_path()
        self.set_file_path()

    def set_folder_path(self):
        path = os.path.join(self.data_set_obj.results_path,
                            "Envelope Trends")
        self.data_set_obj.envelope_trends_path = path
        make_folder(path, message=True)

    def set_file_path(self):
        self.path = os.path.join(self.data_set_obj.envelope_trends_path,
                                 "Envelope Trends")

    def create_plot(self):
        self.ensure_loaded()
        lines_objects = self.get_lines_objects()
        self.plots_obj = Plots(lines_objects)
        self.plots_obj.plot()

    def get_lines_objects(self):
        lines_obj_gradient = self.get_lines_obj_gradient()
        lines_obj_intercept = self.get_lines_obj_intercept()
        lines_objects = [lines_obj_gradient, lines_obj_intercept]
        return lines_objects

    def get_lines_obj_gradient(self):
        line_objects = [self.get_line_object_gradient(drift_obj)
                        for drift_obj in self.data_set_obj.drift_objects]
        lines_obj = Lines(line_objects)
        return lines_obj

    def get_line_object_gradient(self, drift_obj):
        x_values = [detuning_obj.detuning for detuning_obj in drift_obj.detuning_objects]
        y_values = [detuning_obj.gradient_mean for detuning_obj in drift_obj.detuning_objects]
        deviations = [detuning_obj.gradient_deviation for detuning_obj in drift_obj.detuning_objects]
        label = drift_obj.drift_value
        line_obj = Line(x_values, y_values, label=label)
        line_obj.deviations = deviations
        return line_obj
    
    def get_lines_obj_intercept(self):
        line_objects = [self.get_line_object_intercept(drift_obj)
                        for drift_obj in self.data_set_obj.drift_objects]
        lines_obj = Lines(line_objects)
        return lines_obj

    def get_line_object_intercept(self, drift_obj):
        x_values = [detuning_obj.detuning for detuning_obj in drift_obj.detuning_objects]
        y_values = [detuning_obj.intercept_mean for detuning_obj in drift_obj.detuning_objects]
        deviations = [detuning_obj.intercept_deviation for detuning_obj in drift_obj.detuning_objects]
        label = drift_obj.drift_value
        line_obj = Line(x_values, y_values, label=label)
        line_obj.deviations = deviations
        return line_obj

    def ensure_loaded(self):
        if not self.loaded:
            self.execute("Load")
