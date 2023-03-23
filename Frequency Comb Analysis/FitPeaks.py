import numpy as np
import scipy.optimize as sc

from PeakLine import PeakLine

class FitPeaks():

    def __init__(self, group_obj):
        self.group_obj = group_obj
        self.spectrum_obj = self.group_obj.spectrum_obj
        self.set_peak_data()

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
        function_values = evaluate_abs(self.peak_frequencies, fitting_parameters)
        residuals = function_values - self.peak_S21s_log
        return residuals

    def get_initial_fitting_parameters(self):
        gradient = 1
        intercept = max(self.peak_S21s)
        initial_fitting_parameters = [gradient, intercept]
        return initial_fitting_parameters

    def set_values_fit(self, x_values, fitting_parameters):
        self.x_values_fit = np.array([self.spectrum_obj.frequency[0], 0, self.spectrum_obj.frequency[-1]])
        self.y_values_fit = evaluate_abs(self.x_values_fit, fitting_parameters)

def evaluate_abs(x_values, fitting_parameters, centre=0):
    gradient, y_intercept = fitting_parameters
    left_gradient = abs(gradient)
    right_gradient = -1*left_gradient
    left_x_values = x_values[x_values < centre]
    right_x_values = x_values[x_values >= centre]
    left_function_values = left_gradient*left_x_values + y_intercept
    right_function_values = right_gradient*right_x_values + y_intercept
    function_values = np.concatenate((left_function_values, right_function_values))
    return function_values

