import os
import numpy as np
import scipy as sc
import math
import matplotlib.pyplot as plt
from DataFit import DataFit

class Data():

    """
    This class handles all the data for S21 and frequency pair.
    This could be a spectrum, a transmission, or an average of several spectra.

    Spectrum and Transmission are subclasses of this.
    """

    semi_width = 150
    large_peak_threshold = 10**-8
    peak_ratio_threshold = 11.5
    review_centre_heuristic_plot = False
    review_centre_results_plot = False
    suppress_centre_computation_warnings = True
    
    def __init__(self, detuning_obj):
        self.detuning_obj = detuning_obj
        self.detuning = detuning_obj.detuning
        self.power = self.detuning_obj.trial.power
        self.timestamp = self.detuning_obj.timestamp

    def process_S21(self):
        self.set_S21()
        self.set_S21_has_valid_peak()
        if self.S21_has_valid_peak:
            self.set_S21_centre_index()

    def set_S21(self):
        voltage = self.get_voltage_from_file()
        voltage = (10**(voltage/10))/1000
        self.S21 = voltage/self.power

    def get_voltage_from_file(self):
        with open(self.file_path, "r") as file:
            file.readline()
            voltage = [self.get_voltage_from_file_line(line)
                       for line in file]
        return np.array(voltage)

    def get_voltage_from_file_line(self, line):
        line_components = line.strip().split("\t")
        try:
            voltage = float(line_components[0])
            return voltage
        except:
            raise Exception((f"Could not read voltage from file line '{line}'"
                             f"while attempting to process spectrum:\n{self}"))

    def set_S21_centre_index(self):
        if self.if_large_peak():
            self.set_S21_centre_index_large()
        else:
            self.set_S21_centre_index_small()

    def if_large_peak(self):
        peak_is_large = (np.max(self.S21) > self.large_peak_threshold)
        data_not_transmission = (type(self) != "<class 'Transmission.Transmission'>")
        return (peak_is_large and data_not_transmission)

    def set_S21_centre_index_large(self):
        self.peak_index = np.argmax(self.S21)
        self.S21_centre_index = self.peak_index
        self.set_S21_centre_frequency()

    def set_S21_centre_index_small(self):
        self.peak_index = np.argmax(self.S21)
        candidate_indexes, region_points = self.get_candidate_and_region_indexes()
        uncentred_heuristics = self.get_uncentred_heuristics(candidate_indexes, region_points)
        heuristic_intercept_x, heuristic_intercept_y = self.process_uncentred_heuristics(candidate_indexes, uncentred_heuristics)
        self.S21_centre_index = round(heuristic_intercept_x)
        self.set_S21_centre_frequency()
        self.review_centre()

    def get_candidate_and_region_indexes(self):
        spacing = 4
        left_limit = self.get_left_limit()
        right_limit = self.get_right_limit()
        region_points = np.array(range(left_limit, right_limit))
        candidate_indexes = region_points[[0, spacing, -spacing-1, -1]]
        return candidate_indexes, region_points

    def get_left_limit(self):
        left_limit = self.peak_index - self.semi_width
        if left_limit < 0:
            self.warning_computation_of_centre("left")
            left_limit = 0
        return left_limit

    def get_right_limit(self):
        right_limit = self.peak_index + self.semi_width
        if right_limit >= len(self.S21):
            self.warning_computation_of_centre("right")
            right_limit = len(self.S21)
        return right_limit

    def warning_computation_of_centre(self, side):
        if self.suppress_centre_computation_warnings == False:
            print((f"WARNING: peak is near {side} side of range.\n"
                   f"Computation of centre may be compromised.\n"
                   f"Spectrum details: {self.file_path}"))

    def get_uncentred_heuristics(self, candidate_indexes, region_points):
        uncentred_heuristic = [self.get_uncentred_heuristic(point, region_points)
                               for point in candidate_indexes]
        return uncentred_heuristic

    def get_uncentred_heuristic(self, point, region_points):
        widths = abs(point - region_points)
        heights = self.S21[region_points]
        uncentred_heuristic = sum(widths*heights**2)
        return uncentred_heuristic

    def process_uncentred_heuristics(self, candidate_indexes, uncentred_heuristics):
        x_values_left, y_values_left = candidate_indexes[:2], uncentred_heuristics[:2]
        x_values_right, y_values_right = candidate_indexes[-2:], uncentred_heuristics[-2:]
        a_left, b_left, c_left = self.get_linear_equation_coefficients(x_values_left, y_values_left)
        a_right, b_right, c_right = self.get_linear_equation_coefficients(x_values_right, y_values_right)
        discriminant = a_left*b_right - a_right*b_left
        x = (b_right*c_left - b_left*c_right)/discriminant
        y = (a_left*c_left - a_right*c_right)/(a_left*b_right - a_right*b_left)
        return x, y

    def get_linear_equation_coefficients(self, x_values, y_values):
        x_1, x_2 = x_values
        y_1, y_2 = y_values
        a, b = y_2 - y_1, x_1 - x_2
        c = a*x_1 + b*y_1
        return a, b, c

    def set_S21_centre_frequency_peak(self):
        self.S21_centre_frequency = self.frequency[self.peak_index]
    
    def set_S21_centre_frequency_index(self):
        self.S21_centre_frequency = self.frequency[self.S21_centre_index]

    def set_S21_centre_frequency_lorentzian_fit(self, width=10):
        self.remove_S21_discontinuities()
        data_fit_obj = DataFit(self)
        self.fit_function = data_fit_obj.evaluate_lorentzian
        initial_fitting_parameters = data_fit_obj.get_initial_fitting_parameters()
        self.fit_width = width
        self.fitting_parameters = data_fit_obj.get_automatic_fit(initial_fitting_parameters)
        self.S21_centre_frequency = self.fitting_parameters[3]

    def set_S21_centre_frequency_polynomial_fit(self, degree=2, width=10):
        self.remove_S21_discontinuities()
        data_fit_obj = DataFit(self)
        self.fit_function = data_fit_obj.evaluate_polynomial
        initial_fitting_parameters = np.zeros(degree + 1)
        self.fit_width = width
        self.fitting_parameters = data_fit_obj.get_automatic_fit(initial_fitting_parameters)
        points = np.linspace(self.fit_frequencies[0], self.fit_frequencies[-1], 100)
        self.S21_centre_frequency = points[round(np.argmax(np.polyval(self.fitting_parameters, points)))]

    def review_centre(self):
        self.if_review_centre_heuristic()
        self.if_review_centre_results()

    def if_review_centre_heuristic(self):
        if self.review_centre_heuristic_plot:
            self.review_centre_heuristic()

    def review_centre_heuristic(self):
        candidate_indexes, region_points = self.get_candidate_and_region_indexes()
        uncentred_heuristics = self.get_uncentred_heuristics(candidate_indexes, region_points)
        _, heuristic_intercept = self.process_uncentred_heuristics(candidate_indexes, uncentred_heuristics)
        self.output_review_centre_heuristic(candidate_indexes, region_points, heuristic_intercept)

    def output_review_centre_heuristic(self, candidate_indexes, region_points, heuristic_intercept):
        self.output_centre_data(candidate_indexes, region_points)
        self.plot_review_centre_heuristic(region_points, candidate_indexes, heuristic_intercept)
        self.add_review_centre_heuristic_labels()
        plt.show()

    def output_centre_data(self, candidate_indexes, region_points):
        print((f"Peak index: {self.peak_index}\n"
               f"Frequency min, max, and len: {min(self.frequency)}, {max(self.frequency)}, {len(self.frequency)}\n"
               f"S21 len: {len(self.S21)}\n"
               f"Candidate indices: {candidate_indexes}\n"
               f"Region points: {region_points}\n"))
    
    def get_review_heuristics_data(self, region_points):
        filter_indices = list(range(0, len(region_points), 4))
        filter_indices = sorted(list(set(filter_indices + [len(region_points) - 1])))
        region_points_filtered = [region_points[i] for i in filter_indices]
        uncentred_heuristics = self.get_uncentred_heuristics(region_points_filtered,
                                                             region_points)
        return region_points_filtered, uncentred_heuristics

    def plot_review_centre_heuristic(self, region_points, candidate_indexes, heuristic_intercept):
        plt.plot(*self.get_review_heuristics_data(region_points))
        plt.plot(self.S21_centre_index, heuristic_intercept, 'b*')
        for index in candidate_indexes:
            plt.plot(index, self.get_uncentred_heuristic(index, region_points), 'r*')

    def add_review_centre_heuristic_labels(self):
        power_folder = self.detuning_obj.trial.power_obj.folder_name
        trial = self.detuning_obj.trial.trial_number
        plt.xlabel("Index")
        plt.ylabel("Centre heuristic value")
        plt.title((f"Computation of centre of data for\n"
                   f"power {power_folder}, trial {trial}, detuning {self.detuning}"))

    def if_review_centre_results(self):
        if self.review_centre_results_plot:
            self.review_centre_results()

    def review_centre_results(self):
        _, region_points = self.get_candidate_and_region_indexes()
        self.add_plot_of_fit()
        self.output_review_centre_results(region_points)

    def add_plot_of_fit(self):
        plot_obj = DataFit(self)
        plot_obj.plot_fitting(fitting=True)

    def output_review_centre_results(self, region_points):
        plt.plot(self.frequency, self.S21)
        frequency_range = np.linspace(0, self.S21[self.peak_index], 100)
        plt.plot(self.frequency[self.peak_index], self.S21[self.peak_index], '*k')
        plt.plot([self.S21_centre_frequency] * 100, frequency_range, 'r')
        self.add_review_centre_results_labels()
        plt.show()
    
    def add_review_centre_results_labels(self):
        power_folder = self.detuning_obj.trial.power_obj.folder_name
        trial = self.detuning_obj.trial.trial_number
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("S21")
        plt.title((f"Computation of centre of data for\n"
                   f"power {power_folder}, trial {trial}, detuning {self.detuning}"))

    def get_S21_centre_index(self):
        if self.S21_has_valid_peak:
            return self.S21_centre_index
        else:
            return None

    def get_S21_centre_frequency(self):
        if self.S21_has_valid_peak:
            return self.S21_centre_frequency
        else:
            return None

    def set_amplitude_from_fit(self):
        function_values = self.fit_function(self.fitting_parameters)
        self.amplitude = max(function_values)

    def plot_S21(self, fitting=False):
        plot_obj = DataFit(self)
        plot_obj.plot_S21(fitting)

    def __str__(self):
        string = (f"Detuning: {self.detuning}\n"
                  f"Power: {self.power}\n"
                  f"Timestamp: {self.timestamp}\n"
                  f"File path: {self.file_path}\n")
        return string
