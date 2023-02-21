import os
import time
import numpy as np
import scipy as sc
import math
import matplotlib.pyplot as plt

class Data():

    """
    This class handles all the data for S21 and frequency pair.
    This could be a spectrum, a transmission, or an average of several spectra.

    Spectrum and Transmission are subclasses of this.
    """

    peak_ratio_threshold = 11.5
    review_centre_heuristic_plot = False
    review_centre_results_plot = False
    suppress_centre_computation_warnings = True
    reject_bad_fits = False
    bad_fit_threshold = 2000
    parameter_names = ["F", "Gamma", "Noise", "w"]
    
    def __init__(self, detuning_obj):
        self.detuning_obj = detuning_obj
        self.detuning = detuning_obj.detuning
        self.power = self.detuning_obj.trial.power
        self.timestamp = self.detuning_obj.timestamp
        self.set_fitting_choice_functions()

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

    def set_S21_has_valid_peak(self):
        peak = np.max(self.S21)
        noise = np.median(self.S21)
        peak_ratio = peak / noise
        self.S21_has_valid_peak = (peak_ratio > self.peak_ratio_threshold)

    def set_S21_centre_index(self):
        peak_index = np.argmax(self.S21)
        candidate_indexes, region_points = self.get_candidate_and_region_indexes(peak_index)
        uncentred_heuristics = self.get_uncentred_heuristics(candidate_indexes, region_points)
        heuristic_intercept_x, heuristic_intercept_y = self.process_uncentred_heuristics(candidate_indexes, uncentred_heuristics)
        self.S21_centre_index = round(heuristic_intercept_x)
        self.set_S21_centre_frequency_fit()
        self.review_centre()

    def get_candidate_and_region_indexes(self, peak_index):
        spacing = 4
        left_limit = self.get_left_limit(peak_index)
        right_limit = self.get_right_limit(peak_index)
        region_points = np.array(range(left_limit, right_limit))
        candidate_indexes = region_points[[0, spacing, -spacing-1, -1]]
        return candidate_indexes, region_points

    def get_left_limit(self, peak_index):
        left_limit = peak_index - self.semi_width
        if left_limit < 0:
            self.warning_computation_of_centre("left")
            left_limit = 0
        return left_limit

    def get_right_limit(self, peak_index):
        right_limit = peak_index + self.semi_width
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

    def set_S21_centre_frequency_index(self):
        self.S21_centre_frequency = self.frequency[self.S21_centre_index]

    def set_S21_centre_frequency_interpolate(self, heuristic_intercept):
        lower_index = math.floor(heuristic_intercept)
        upper_index = math.ceil(heuristic_intercept)
        lower_frequency = self.frequency[lower_index]
        upper_frequency = self.frequency[upper_index]
        fractional_part = heuristic_intercept % 1
        self.S21_centre_frequency = lower_frequency + (upper_frequency - lower_frequency)*fractional_part

    def set_S21_centre_frequency_fit(self):
        initial_fitting_parameters = self.get_initial_fitting_parameters()
        fitting_parameters = self.get_automatic_fit(initial_fitting_parameters)
        self.S21_centre_frequency = fitting_parameters[3]

    def review_centre(self):
        self.if_review_centre_heuristic()
        self.if_review_centre_results()

    def if_review_centre_heuristic(self):
        if self.review_centre_heuristic_plot:
            self.review_centre_heuristic()

    def review_centre_heuristic(self):
        peak_index = np.argmax(self.S21)
        candidate_indexes, region_points = self.get_candidate_and_region_indexes(peak_index)
        uncentred_heuristics = self.get_uncentred_heuristics(candidate_indexes, region_points)
        _, heuristic_intercept = self.process_uncentred_heuristics(candidate_indexes, uncentred_heuristics)
        self.output_review_centre_heuristic(peak_index, candidate_indexes, region_points, heuristic_intercept)

    def output_review_centre_heuristic(self, peak_index, candidate_indexes, region_points, heuristic_intercept):
        self.output_centre_data(peak_index, candidate_indexes, region_points)
        self.plot_review_centre_heuristic(region_points, candidate_indexes, heuristic_intercept)
        self.add_review_centre_heuristic_labels()
        plt.show()

    def output_centre_data(self, peak_index, candidate_indexes, region_points):
        print((f"Peak index: {peak_index}\n"
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
        peak_index = np.argmax(self.S21)
        _, region_points = self.get_candidate_and_region_indexes(peak_index)
        self.output_review_centre_results(peak_index, region_points)

    def output_review_centre_results(self, peak_index, region_points):
        plt.plot(self.frequency, self.S21)
        frequency_range = np.linspace(0, self.S21[peak_index], 100)
        plt.plot(self.frequency[peak_index], self.S21[peak_index], '*k')
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

    def set_fitting_choice_functions(self):
        self.fitting_choice_functions = {"1": (self.update_fitting_parameter, 0),
                                         "2": (self.update_fitting_parameter, 1),
                                         "3": (self.update_fitting_parameter, 2),
                                         "4": (self.update_fitting_parameter, 3),
                                         "5": (self.reset_fitting_parameters, ),
                                         "6": (self.update_all_fitting_parameters, ),
                                         "7": (self.reattempt_automatic_fit, ),
                                         "8": (self.accept_fit, ),
                                         "": (self.reject_fit, )}

    def get_initial_fitting_parameters(self):
        end = int(len(self.S21)/5)
        noise = np.mean(self.S21[:end])
        w = self.frequency[np.argmax(self.S21)]
        K = np.mean(self.S21[self.S21 >= np.max(self.S21)*2/3])
        k = K * 1/2
        frequency_resolution = self.frequency[1] - self.frequency[0]
        peak_points = [self.S21 > k]
        width = 2 * (np.count_nonzero(peak_points) + 1)*frequency_resolution
        gamma = width * math.sqrt(k/(K-k))
        F = gamma**2 * K * 2/3
        initial_fitting_parameters = [F, gamma, noise, w]
        return initial_fitting_parameters

    def get_automatic_fit(self, initial_fitting_parameters):
        fitting_parameters = sc.optimize.leastsq(self.get_residuals,
                                                 initial_fitting_parameters)[0]
        return fitting_parameters

    def get_residuals(self, fitting_parameters):
        residuals = self.evaluate_lorentzian(fitting_parameters) - self.S21
        return residuals

    def evaluate_lorentzian(self, lorentzian_parameters):
        F, gamma, noise, w = lorentzian_parameters
        function_values = (F/(gamma**2 + 4*(self.frequency - w)**2)) + noise
        return function_values

    def get_gamma_from_fit(self):
        if self.is_plot_badly_fitted():
            fit_rejected = self.fit_plot_manually_filter()
            if fit_rejected:
                return None
        gamma = abs(self.fitting_parameters[1])
        return gamma

    def is_plot_badly_fitted(self):
        fit_heuristic = self.get_fit_heuristic()
        if fit_heuristic > self.bad_fit_threshold:
            if self.reject_bad_fits == False:
                print(f"Fit heuristic: {fit_heuristic}")
            return True
        return False

    def get_fit_heuristic(self):
        fit_ratio = abs(self.fitting_parameters[:1]/np.array(self.initial_fitting_parameters[:1]))
        fit_heuristic = sum(fit_ratio + 1/fit_ratio)
        return fit_heuristic

    def fit_plot_manually_filter(self):
        if self.reject_bad_fits:
            print("Rejecting fit")
            return None
        else:
            return self.fit_plot_manually()

    def fit_plot_manually(self):
        continue_looping = True
        while continue_looping:
            self.output_fitting_parameters()
            self.plot_S21(fitting = True)
            continue_looping, fit_rejected = self.fit_plot_manually_iteration()

    def fit_plot_manually_iteration(self):
        fitting_input_choice = self.get_fitting_input_choice()
        continue_looping, fit_rejected = self.execute_manual_fit_choice(fitting_input_choice)
        return continue_looping, fit_rejected

    def get_fitting_input_choice(self):
        prompt = ("\nWhich option do you want to change?\n1: F\n2: Gamma\n3: Noise\n" +
                  "4: w\n5: Reset to default\n6: Change all at once\n" +
                  "7: Attempt automatic fit\n8: Accept\nNo input: Reject\n")
        fitting_input_choice = input(prompt)
        return fitting_input_choice

    def execute_manual_fit_choice(self, fitting_input_choice):
        if fitting_input_choice in self.fitting_choice_functions:
            a = self.fitting_choice_functions[fitting_input_choice]
            fitting_choice_function, *args = self.fitting_choice_functions[fitting_input_choice]
            continue_looping, fit_rejected = fitting_choice_function(*args)
        else:
            print("Sorry, you must choose one of the options. Try again.")
            continue_looping, fit_rejected = True, None
        return continue_looping, fit_rejected

    def update_fitting_parameter(self, parameter_index):
        parameter_index = int(parameter_index)
        prompt = f"\nWhat is the new value of '{self.parameter_names[parameter_index]}': "
        try:
            new_parameter_value = float(input(prompt))
            self.fitting_parameters[parameter_index] = new_parameter_value
        except:
            print("Sorry, that didn't work")
        return True, None

    def reset_fitting_parameters(self):
        self.fitting_parameters = self.get_initial_fitting_parameters()
        continue_looping = True
        fit_rejected = None
        return continue_looping, fit_rejected

    def update_all_fitting_parameters(self):
        prompt = "Enter all the new values in a list separated by spaces\n"
        self.set_all_fitting_parameters(prompt)
        continue_looping = True
        fit_rejected = None
        return continue_looping, fit_rejected

    def set_all_fitting_parameters(self, prompt):
        input_rejected = True
        while input_rejected:
            self.fitting_parameters, input_rejected = self.get_all_fitting_parameters(prompt)
            input_rejected = self.check_if_4_fitting_parameters(input_rejected)

    def get_all_fitting_parameters(self, prompt):
        try:
            fitting_parameters, input_wrong = self.attempt_get_fitting_parameters(prompt)
        except:
            fitting_parameters, input_wrong = self.failed_attempt_fitting_parameters()
        return fitting_parameters, input_wrong

    def attempt_get_fitting_parameters(self, prompt):
        fitting_parameters = [float(parameter_input)
                              for parameter_input in input(prompt).split(" ")]
        input_wrong = False
        return fitting_parameters, input_wrong

    def failed_attempt_fitting_parameters(self):        
        print("Sorry, you typed it in wrong, try again")
        fitting_parameters = self.fitting_parameters
        input_wrong = True
        return fitting_parameters, input_wrong

    def check_if_4_fitting_parameters(self, input_rejected):
        if self.fitting_parameters is not None:
            if len(self.fitting_parameters) != 4:
                input_rejected = True
                print("Sorry, you must enter 4 parameters")
        return input_rejected

    def reattempt_automatic_fit(self):
        self.fitting_parameters = self.get_automatic_fit(self.fitting_parameters)
        continue_looping = True
        fit_rejected = None
        return continue_looping, fit_rejected

    def accept_fit(self):
        continue_looping = False
        fit_rejected = False
        return continue_looping, fit_rejected

    def reject_fit(self):
        continue_looping = False
        fit_rejected = True
        return continue_looping, fit_rejected

    def output_fitting_parameters(self):
        parameter_tuples = zip(self.parameter_names, self.fitting_parameters)
        for parameter_name, parameter_value in parameter_tuples:
            print(f"{parameter_name}: {parameter_value}")

    def plot_S21(self, fitting=False):
        plt.figure()
        plt.plot(self.frequency, self.S21, '.', alpha = 1)
        self.plot_fitting(fitting)
        self.add_plot_labels()
        plt.show()

    def plot_fitting(self, fitting):
        if fitting is True and self.fitting_parameters is not None:
            plt.plot(self.frequency,
                     self.evaluate_lorentzian(self.fitting_parameters),
                     'k--', alpha=0.5, linewidth=2.0, label='fit')

    def add_plot_labels(self):
        plt.title("My Title")
        x_ticks = plt.xticks()[0]
        max_x_tick = max(abs(x_ticks))
        prefix_power = math.floor(math.log(max_x_tick, 1000))
        prefix = {-1: "mHz", 0: "Hz", 1: "kHz", 2: "MHz", 3: "GHz", 4: "THz"}[prefix_power]
        x_labels = [f'{value:.3f}' for value in plt.xticks()[0]/1000**prefix_power]
        plt.xticks(x_ticks, x_labels)
        plt.xlabel('${\omega_c}$' + f'({prefix})')
        plt.ylabel('Amplitude')

    def __str__(self):
        string = (f"Detuning: {self.detuning}\n"
                  f"Power: {self.power}\n"
                  f"Timestamp: {self.timestamp}\n"
                  f"File path: {self.file_path}\n")
        return string
