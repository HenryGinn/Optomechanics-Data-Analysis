import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from DataFit import DataFit
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path
from Utils import get_moving_average

class SpectrumCentre(Feature):

    name = "Spectrum Centre"

    def __init__(self, data_set_obj):
        Feature.__init__(self, data_set_obj)
        self.set_commands()
    
    def set_paths(self):
        self.set_folder_path()
        for power_obj in self.data_set_obj.power_objects:
            self.set_power_path(power_obj)
            self.set_trial_paths(power_obj)

    def set_power_path(self, power_obj):
        path = os.path.join(self.folder_path, power_obj.power_string)
        power_obj.spectra_centre_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)
            self.set_detuning_paths(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.spectra_centre_path, f"Trial {trial_obj.trial_number}")
        trial_obj.spectra_centre_path = path
        make_folder(path)

    def set_detuning_paths(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.trial_obj.spectra_centre_path, f"{detuning_obj.detuning} Hz.txt")
        detuning_obj.spectra_centre_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.spectra_valid("Load")

    def save_data_set_obj(self, data_set_obj):
        for power_obj in data_set_obj.power_objects:
            self.save_power_obj(power_obj)

    def save_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.save_trial_obj(trial_obj)

    def save_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_obj(detuning_obj)
            self.save_detuning_obj(detuning_obj)

    def set_detuning_obj(self, detuning_obj):
        for spectrum_obj in detuning_obj.spectrum_objects:
            self.set_spectrum_obj(spectrum_obj)

    def set_spectrum_obj(self, spectrum_obj):
        if spectrum_obj.has_valid_peak:
            self.do_set_spectrum_obj(spectrum_obj)
        else:
            spectrum_obj.fitting_parameters = None

    def do_set_spectrum_obj(self, spectrum_obj):
        spectrum_obj.load_S21()

    def save_detuning_obj(self, detuning_obj):
        with open(detuning_obj.spectra_centre_path, "w") as file:
            file.writelines("Spectrum Index\tF\tGamma\tNoise\tResonant\n")
            self.save_detuning_obj_to_file(detuning_obj, file)

    def save_detuning_obj_to_file(self, detuning_obj, file):
        for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
            if spectrum_obj.has_valid_peak:
                self.save_spectrum_obj_to_file(spectrum_obj, index, file)

    def save_spectrum_obj_to_file(self, spectrum_obj, index, file):
        pass

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.spectra_centre_path)
                       for power_obj in self.data_set_obj.power_objects
                       for trial_obj in power_obj.trial_objects
                       for detuning_obj in trial_obj.detuning_objects])

    def do_load_data(self):
        for power_obj in self.data_set_obj.power_objects:
            self.load_power_obj(power_obj)

    def load_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.load_trial_obj(trial_obj)

    def load_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.load_detuning_obj(detuning_obj)

    def load_detuning_obj(self, detuning_obj):
        file_contents = get_file_contents_from_path(detuning_obj.spectra_centre_path)



    def set_S21_centre_index_small(self):
        self.peak_index = np.argmax(self.S21)
        candidate_indexes, region_points = self.get_candidate_and_region_indexes()
        uncentred_heuristics = self.get_uncentred_heuristics(candidate_indexes, region_points)
        heuristic_intercept_x, heuristic_intercept_y = self.process_uncentred_heuristics(candidate_indexes, uncentred_heuristics)
        self.S21_centre_index = round(heuristic_intercept_x)
        self.peak_frequency = self.frequency[self.S21_centre_index]
        self.peak_S21 = self.S21[self.S21_centre_index]
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

    def set_peak_frequency_peak(self):
        self.peak_frequency = self.frequency[self.peak_index]
    
    def set_peak_frequency_index(self):
        self.peak_frequency = self.frequency[self.peak_index]

    def set_peak_frequency_lorentzian_fit(self, width=10):
        data_fit_obj = DataFit(self)
        self.fit_function = self.evaluate_lorentzian
        initial_fitting_parameters = data_fit_obj.get_initial_fitting_parameters()
        self.fit_width = width
        self.fitting_parameters = data_fit_obj.get_automatic_fit(initial_fitting_parameters)
        self.peak_frequency = self.fitting_parameters[3]

    def set_peak_frequency_polynomial_fit(self, degree=2, width=10):
        self.remove_S21_discontinuities()
        data_fit_obj = DataFit(self)
        self.fit_function = self.evaluate_polynomial
        initial_fitting_parameters = np.zeros(degree + 1)
        self.fit_width = width
        self.fitting_parameters = data_fit_obj.get_automatic_fit(initial_fitting_parameters)
        points = np.linspace(self.fit_frequencies[0], self.fit_frequencies[-1], 100)
        self.peak_frequency = points[round(np.argmax(np.polyval(self.fitting_parameters, points)))]

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
        plt.plot(self.peak_index, heuristic_intercept, 'b*')
        for index in candidate_indexes:
            plt.plot(index, self.get_uncentred_heuristic(index, region_points), 'r*')

    def add_review_centre_heuristic_labels(self):
        power_folder = self.detuning_obj.trial_obj.power_obj.folder_name
        trial = self.detuning_obj.trial_obj.trial_number
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
        if self.detuning_obj.review_all_S21_simultaneously:
            plt.subplot()
        self.output_review_centre_results_single(region_points)
        if self.detuning_obj.review_all_S21_simultaneously is False:
            plt.show()

    def output_review_centre_results_single(self, region_points):
        plt.plot(self.frequency, self.S21)
        frequency_range = np.linspace(0, self.S21[self.peak_index], 100)
        plt.plot(self.frequency[self.peak_index], self.S21[self.peak_index], '*k')
        plt.plot([self.peak_frequency] * 100, frequency_range, 'r')
        self.add_review_centre_results_labels()
    
    def add_review_centre_results_labels(self):
        power_folder = self.detuning_obj.trial_obj.power_obj.folder_name
        trial = self.detuning_obj.trial_obj.trial_number
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("S21")
        plt.title((f"Computation of centre of data for\n"
                   f"power {power_folder}, trial {trial}, detuning {self.detuning}"))
