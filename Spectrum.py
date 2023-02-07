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
        self.set_find_centre()

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
        candidate_indexes = self.get_candidate_indexes(peak_index)
        uncentred_heuristics = self.get_uncentred_heuristics(candidate_indexes)
        self.S21_centre_index = self.process_uncentred_heuristics(uncentred_heuristics)

    def get_candidate_indexes(self, peak_index):
        semi_width, spacing = 150, 4
        left_limit = self.get_left_limit(peak_index, semi_width)
        right_limit = self.get_right_limit(peak_index, semi_width)
        candidate_indexes = list(range(left_limit, right_limit, spacing))
        return candidate_indexes

    def get_left_limit(self, peak_index, semi_width):
        left_limit = peak_index - semi_width
        if left_limit < 0:
            print(("WARNING: peak is near left side of range.\n
                   "Computation of centre may be compromised\n"
                   f"Spectrum details: {self.spectrum_path}")
            left_limit = 0
        return left_limit

    def get_right_limit(self, peak_index, semi_width):
        right_limit = peak_index + semi_width
        if right_limit >= len(self.S21):
            print(("WARNING: peak is near right side of range.\n
                   "Computation of centre may be compromised\n"
                   f"Spectrum details: {self.spectrum_path}")
            right_limit = 0
        return right_limit

##################################################################################################################

    def get_index_maximum(S21):
        """
        We get a ballpark guess of where the peak is by using argmax Around this
        point we find assign a value to how good that point would work as the centre
        of the points using a weighted sum. The worse the point is, the higher the
        value of the heuristic. We get something that looks like y=|x| but with a
        rounded bottom. Using the data in the rounded region was less robust, so we
        define two lines from each side of the bottom in the region where the
        heuristic is better behaved and find where they intersect. This point is
        used as the centre.
        """
        first_guess = argmax(S21)
        left_x, right_x = max(0, first_guess-150), min(first_guess+150, len(S21)-1)
        candidates = list(range(left_x, right_x, 4))
        points = array(range(left_x, right_x))
        uncentred_heuristics = [get_uncentred_heuristic(S21, x, points) for x in candidates]
        m = argmin(uncentred_heuristics)
        x_m, y_m = get_heuristic_line_intersection(m, uncentred_heuristics)
        #plot_index_max_heuristic(candidates, uncentred_heuristics, x_m, y_m,
        #                         x_1, x_2, x_3, x_4, y_1, y_2, y_3, y_4)
        return candidates[x_m]

    def get_uncentred_heuristic(S21, x, points):
        uncentred_heuristic = abs(x-points)*(S21[points])**2
        uncentred_heuristic = sum(uncentred_heuristic)
        return uncentred_heuristic

    def get_heuristic_line_intersection(m, uncentred_heuristics):
        x_1, x_2, x_3, x_4 = m-15, m-14, m+14, m+15
        y_1, y_2, y_3, y_4 = (uncentred_heuristics[x] for x in [x_1, x_2, x_3, x_4])
        a, b, e = y_2-y_1, x_1-x_2, x_1*(y_2-y_1)+y_1*(x_1-x_2)
        c, d, f = y_4-y_3, x_3-x_4, x_3*(y_4-y_3)+y_3*(x_3-x_4)
        x_m = math.floor((d*e-b*f)/(a*d-b*c))
        y_m = (-c*e+a*f)/(a*d-b*c)
        return x_m, y_m

##################################################################################################################        

    def __str__(self):
        string = (f"Detuning: {self.detuning}\n"
                  f"Power: {self.power}\n"
                  f"Timestamp: {self.timestamp}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum path: {self.spectrum_path}\n")
        return string
