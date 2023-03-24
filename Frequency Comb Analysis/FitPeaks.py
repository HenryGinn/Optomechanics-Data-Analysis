import numpy as np
import scipy.optimize as sc

from PeakLine import PeakLine

class FitPeaks():

    def __init__(self, group_obj):
        self.group_obj = group_obj

    def set_peak_data(self):
        self.peak_indices = self.spectrum_obj.peak_indices
        self.peak_frequencies = self.spectrum_obj.peak_frequencies
        self.peak_S21s = self.spectrum_obj.peak_S21s
        self.peak_S21s_log = np.log(self.peak_S21s)

    def fit_peaks(self):
        initial_fitting_parameters = self.get_initial_fitting_parameters()
        self.fitting_parameters = sc.leastsq(self.get_residuals,
                                             initial_fitting_parameters)[0]
        
    def get_residuals(self, fitting_parameters):
        function_values = self.evaluate_abs(self.peak_frequencies, fitting_parameters)
        residuals = function_values - self.peak_S21s_log
        return residuals

    def get_initial_fitting_parameters(self):
        gradient = 1
        intercept = max(self.peak_S21s)
        initial_fitting_parameters = [gradient, intercept]
        return initial_fitting_parameters

    def set_envelope_values(self):
        self.set_envelope_x_values()
        self.set_envelope_y_values()

    def set_envelope_x_values(self):
        left_x = self.group_obj.spectrum_obj.peak_frequencies[0]
        right_x = self.group_obj.spectrum_obj.peak_frequencies[-1]
        self.envelope_x_values = np.array([left_x, 0, right_x])

    def set_envelope_y_values(self):
        self.envelope_y_values = evaluate_abs(self.envelope_x_values,
                                              self.fitting_parameters)
        self.envelope_y_values = np.exp(self.envelope_y_values)


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
