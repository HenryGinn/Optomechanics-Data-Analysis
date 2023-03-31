import os

import numpy as np
import scipy.optimize as sc

from CombFunction import CombFunction
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import get_file_contents_from_path

class PeakFits(CombFunction):

    name = "Peak Fits"

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        self.set_folder_path()
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)

    def set_drift_path(self, drift_obj):
        drift_obj.peak_fits_path = os.path.join(self.folder_path,
                                                f"{drift_obj.folder_name}")

    def load_necessary_data_for_saving(self):
        self.data_set_obj.peak_coordinates("Load")

    def save_data_set_obj(self, data_set_obj):
        for drift_obj in data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        self.set_detuning_peaks(drift_obj)
        self.save_peak_fit(drift_obj)

    def set_detuning_peaks(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.set_detuning_peak(detuning_obj)

    def set_detuning_peak(self, detuning_obj):
        self.set_peak_data(detuning_obj)
        self.fit_peaks(detuning_obj)

    def set_peak_data(self, detuning_obj):
        detuning_obj.peak_indices = detuning_obj.spectrum_obj.peak_indices
        detuning_obj.peak_frequencies = detuning_obj.spectrum_obj.peak_frequencies
        detuning_obj.peak_S21s = detuning_obj.spectrum_obj.peak_S21s
        detuning_obj.peak_S21s_log = np.log(detuning_obj.peak_S21s)

    def fit_peaks(self, detuning_obj):
        initial_fitting_parameters = self.get_initial_fitting_parameters(detuning_obj)
        detuning_obj.fitting_parameters = sc.leastsq(self.get_residuals,
                                                     initial_fitting_parameters,
                                                     args=(detuning_obj))[0]
    
    def get_initial_fitting_parameters(self, detuning_obj):
        gradient = 1
        intercept = max(detuning_obj.peak_S21s)
        initial_fitting_parameters = [gradient, intercept]
        return initial_fitting_parameters
        
    def get_residuals(self, fitting_parameters, detuning_obj):
        function_values = evaluate_abs(detuning_obj.peak_frequencies, fitting_parameters)
        residuals = function_values - detuning_obj.peak_S21s_log
        return residuals

    def save_peak_fit(self, drift_obj):
        with open(drift_obj.peak_fits_path, "w") as file:
            file.writelines("Detuning (Hz)\tGradient\tIntercept\n")
            for detuning_obj in drift_obj.detuning_objects:
                self.save_peak_lines_to_file(detuning_obj, file)
    
    def save_peak_lines_to_file(self, detuning_obj, file):
        detuning = detuning_obj.detuning
        gradient = detuning_obj.fitting_parameters[0]
        intercept = detuning_obj.fitting_parameters[1]
        file.writelines(f"{detuning}\t{gradient}\t{intercept}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(drift_obj.peak_fits_path)
                       for drift_obj in self.data_set_obj.drift_objects])

    def do_load_data(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.load_drift_obj(drift_obj)

    def load_drift_obj(self, drift_obj):
        file_contents = zip(*get_file_contents_from_path(drift_obj.peak_fits_path))
        peak_fits_data = {detuning: [gradient, intercept]
                          for detuning, gradient, intercept in file_contents}
        for detuning_obj in drift_obj.detuning_objects:
            detuning_obj.fitting_parameters = peak_fits_data[detuning_obj.detuning]

    def plot(self, **kwargs):
        lines_objects = self.get_lines_objects()
        title = f"{self.data_set_obj} {self.name}"
        self.create_plots(lines_objects, title, kwargs)

    def get_lines_objects(self):
        lines_obj_gradient = self.get_lines_obj_gradient()
        lines_obj_intercept = self.get_lines_obj_intercept()
        lines_objects = [lines_obj_gradient, lines_obj_intercept]
        return lines_objects

    def get_lines_obj_gradient(self):
        line_objects = [self.get_line_objects_gradient(drift_obj)
                        for drift_obj in self.data_set_obj.drift_objects]
        lines_obj_gradient = Lines(line_objects, legend=True)
        lines_obj_gradient = self.set_labels(lines_obj_gradient, "Gradient")
        return lines_obj_gradient

    def get_line_objects_gradient(self, drift_obj):
        label = drift_obj.drift_value
        x_values = [detuning_obj.detuning for detuning_obj in drift_obj.detuning_objects]
        y_values = [detuning_obj.fitting_parameters[0] for detuning_obj in drift_obj.detuning_objects]
        line_obj = Line(x_values, y_values, label=label)
        return line_obj

    def get_lines_obj_intercept(self):
        line_objects = [self.get_line_objects_intercept(drift_obj)
                        for drift_obj in self.data_set_obj.drift_objects]
        lines_obj_intercept = Lines(line_objects, legend=True)
        lines_obj_intercept = self.set_labels(lines_obj_intercept, "Intercept (Hz)")
        return lines_obj_intercept

    def get_line_objects_intercept(self, drift_obj):
        label = drift_obj.drift_value
        x_values = [detuning_obj.detuning for detuning_obj in drift_obj.detuning_objects]
        y_values = [detuning_obj.fitting_parameters[1] for detuning_obj in drift_obj.detuning_objects]
        line_obj = Line(x_values, y_values, label=label)
        return line_obj

    def set_labels(self, lines_obj, y_axis_label):
        lines_obj.x_prefix = ""
        lines_obj.x_label = f"Detuning ({lines_obj.x_prefix}Hz)"
        lines_obj.y_label = y_axis_label
        lines_obj.set_rainbow_lines(value=0.9)
        return lines_obj

    def create_plots(self, lines_objects, title, kwargs):
        plots_obj = Plots(lines_objects, kwargs)
        plots_obj.parent_results_path = self.folder_path
        plots_obj.title = title
        plots_obj.plot()

def evaluate_abs(x_values, fitting_parameters, centre=0):
    gradient, y_intercept = fitting_parameters
    left_function_values = get_left_function_values(x_values, gradient, y_intercept, centre)
    right_function_values = get_right_function_values(x_values, gradient, y_intercept, centre)
    function_values = np.concatenate((left_function_values, right_function_values))
    return function_values

def get_left_function_values(x_values, gradient, y_intercept, centre):
    left_gradient = abs(gradient)
    left_x_values = x_values[x_values < centre]
    left_function_values = left_gradient*left_x_values + y_intercept
    return left_function_values

def get_right_function_values(x_values, gradient, y_intercept, centre):
    right_gradient = -1*abs(gradient)
    right_x_values = x_values[x_values >= centre]
    right_function_values = right_gradient*right_x_values + y_intercept
    return right_function_values
