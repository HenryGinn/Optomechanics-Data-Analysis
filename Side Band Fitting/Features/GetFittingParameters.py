import math

import numpy as np
import scipy.optimize as sc
import matplotlib.pyplot as plt

from Utils import get_moving_average
from Utils import evaluate_lorentzian

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class FittingParameters():

    reject_bad_fits = True
    review_bad_fits = False
    suppress_off_centre_peak_warnings = True
    alpha = 3
    bad_fit_threshold = 0.3*10
    parameter_names = ["F", "Gamma", "Noise", "w"]

    def __init__(self, data_obj):
        self.S21 = get_moving_average(data_obj.S21, 20)
        self.frequency = data_obj.frequency

    def set_fitting_parameters(self):
        self.shift_frequency_left()
        #initial_fitting_parameters = self.get_initial_fitting_parameters()
        initial_fitting_parameters = self.get_initial_fitting_parameters()
        self.fitting_parameters = self.get_automatic_fitting_parameters(initial_fitting_parameters)
        self.shift_frequency_right()

    def shift_frequency_left(self):
        self.frequency_shift = self.frequency[np.argmax(self.S21)]
        self.frequency -= self.frequency_shift

    def shift_frequency_right(self):
        self.frequency += self.frequency_shift
        self.fitting_parameters[3] += self.frequency_shift

    def get_initial_fitting_parameters(self):
        noise = self.get_noise()
        resonant = self.get_resonant()
        F, gamma = self.get_F_and_gamma(noise)
        initial_fitting_parameters = [F, gamma, noise, resonant]
        return initial_fitting_parameters

    def get_initial_fitting_parameters2(self):
        max_value = max(self.S21)
        max_index = np.where(self.S21 == max_value)
        lw = abs(self.S21 - (max(self.S21) * (3/4)))
        index1 = np.where(lw == min(lw))
        app_lw = float(10*abs(self.frequency[max_index[0]] - self.frequency[index1[0]]))
        p0 = [max_value*(app_lw)**2, app_lw, np.mean(self.S21[-100:]), float(self.frequency[max_index[0]+1])]
        return p0

    def get_noise(self):
        end_index = int(len(self.S21)/5)
        noise = np.median(self.S21[:end_index])
        return noise

    def get_resonant(self):
        self.resonant_index = np.argmax(self.S21)
        resonant = self.frequency[self.resonant_index]
        return resonant

    def get_F_and_gamma(self, noise):
        width, approximate_peak = self.get_lorentzian_width_parameters(noise)
        gamma = width / (2 * math.sqrt(self.alpha - 1))
        F = gamma**2 * approximate_peak
        return F, gamma

    def get_lorentzian_width_parameters(self, noise):
        approximate_peak, mid_line_height = self.get_lorentzian_height_parameters(noise)
        frequency_resolution = self.frequency[1] - self.frequency[0]
        peak_points = [self.S21 - noise > mid_line_height]
        width = 2 * (np.count_nonzero(peak_points) + 1) * frequency_resolution
        return width, approximate_peak

    def get_lorentzian_height_parameters(self, noise):
        peak_threshold = min(np.max(self.S21), 3*np.median(self.S21))
        points_around_peak = self.S21[self.S21 >= peak_threshold]
        approximate_peak = np.percentile(points_around_peak, 90) - noise
        mid_line_height = approximate_peak / self.alpha
        return approximate_peak, mid_line_height

    def get_automatic_fitting_parameters(self, initial_fitting_parameters):
        fitting_parameters = sc.leastsq(self.get_residuals,
                                        initial_fitting_parameters)[0]
        return fitting_parameters

    def get_residuals(self, fitting_parameters):
        x_values = self.frequency
        function_values = evaluate_lorentzian(x_values, fitting_parameters)
        residuals = function_values - self.S21
        return residuals


def get_fitting_parameters(data_obj):
    fitting_parameters_obj = FittingParameters(data_obj)
    fitting_parameters_obj.set_fitting_parameters()
    return fitting_parameters_obj.fitting_parameters
