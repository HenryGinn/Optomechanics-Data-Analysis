import os

import numpy as np
import scipy.optimize as sc

from CombFunction import CombFunction
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

    def set_envelope_values(self, detuning_obj):
        self.set_envelope_x_values(detuning_obj)
        self.set_envelope_y_values(detuning_obj)

    def set_envelope_x_values(self, detuning_obj):
        left_x = detuning_obj.peak_frequencies[0]
        right_x = detuning_obj.peak_frequencies[-1]
        detuning_obj.envelope_x_values = np.array([left_x, 0, right_x])

    def set_envelope_y_values(self, detuning_obj):
        detuning_obj.envelope_y_values = evaluate_abs(detuning_obj.envelope_x_values,
                                              detuning_obj.fitting_parameters)
        detuning_obj.envelope_y_values = np.exp(detuning_obj.envelope_y_values)

    def data_is_saved(self):
        return np.all([os.path.exists(drift_obj.peak_fits_path)
                       for drift_obj in self.data_set_obj.drift_objects])

    def do_load_data(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.load_drift_obj(drift_obj)

    def load_drift_obj(self, drift_obj):
        file_contents = zip(*get_file_contents_from_path(drift_obj.peak_fits_path))
        for detuning_obj, file_line in zip(drift_obj.detuning_objects, file_contents):
            _, detuning_obj.gradient, detuning_obj.intercept = file_line

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
