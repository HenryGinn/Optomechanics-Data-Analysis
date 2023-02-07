import os
import numpy as np

class Spectrum():

    """
    This class handles all the data for one spectrum of one detuning for one trial.
    Processing the raw data happens here.
    """
    
    def __init__(self, detuning_obj, spectrum_path):
        self.detuning_obj = detuning_obj
        self.detuning = detuning_obj.detuning
        self.power = self.detuning_obj.trial.power
        self.timestamp = self.detuning_obj.timestamp
        self.transmission_path = self.detuning_obj.transmission_path
        self.frequency = self.detuning_obj.frequency
        self.spectrum_path = spectrum_path

    def process_spectrum(self):
        self.set_S21()
        self.set_S21_centre_index()

    def set_S21(self):
        voltage = self.get_voltage_from_file()
        voltage = (10**(voltage/10))/1000
        self.S21 = voltage/self.power

    def get_voltage_from_file(self):
        with open(self.spectrum_path, "r") as file:
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
        peak_index = np.argmax(self.S21)
        candidate_indexes, region_points = self.get_candidate_and_region_indexes(peak_index)
        uncentred_heuristics = self.get_uncentred_heuristics(candidate_indexes, region_points)
        self.S21_centre_index = self.process_uncentred_heuristics(candidate_indexes, uncentred_heuristics)

    def get_candidate_and_region_indexes(self, peak_index):
        semi_width, spacing = 150, 4
        left_limit = self.get_left_limit(peak_index, semi_width)
        right_limit = self.get_right_limit(peak_index, semi_width)
        region_points = np.array(range(left_limit, right_limit))
        candidate_indexes = region_points[[0, spacing, -spacing-1, -1]]
        return candidate_indexes, region_points

    def get_left_limit(self, peak_index, semi_width):
        left_limit = peak_index - semi_width
        if left_limit < 0:
            print((f"WARNING: peak is near left side of range.\n"
                   f"Computation of centre may be compromised.\n"
                   f"Spectrum details: {self.spectrum_path}"))
            left_limit = 0
        return left_limit

    def get_right_limit(self, peak_index, semi_width):
        right_limit = peak_index + semi_width
        if right_limit >= len(self.S21):
            print(("WARNING: peak is near right side of range.\n"
                   "Computation of centre may be compromised\n"
                   f"Spectrum details: {self.spectrum_path}"))
            right_limit = 0
        return right_limit

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
        a_left, b_left, c_left = self.get_linear_equation_coefficients(candidate_indexes[:2], uncentred_heuristics[:2])
        a_right, b_right, c_right = self.get_linear_equation_coefficients(candidate_indexes[-2:], uncentred_heuristics[-2:])
        discriminant = a_left*b_right - a_right*b_left
        x = (b_right*c_left - b_left*c_right)/discriminant
        # y = (a_left*c_left - a_right*c_right)/(a_left*b_right - a_right*b_left)
        return round(x)

    def get_linear_equation_coefficients(self, x_values, y_values):
        x_1, x_2 = x_values
        y_1, y_2 = y_values
        a, b = y_2 - y_1, x_1 - x_2
        c = a*x_1 + b*y_1
        return a, b, c

    def __str__(self):
        string = (f"Detuning: {self.detuning}\n"
                  f"Power: {self.power}\n"
                  f"Timestamp: {self.timestamp}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum path: {self.spectrum_path}\n")
        return string
