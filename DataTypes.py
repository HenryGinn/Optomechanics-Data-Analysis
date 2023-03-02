import numpy as np
from Data import Data

class Spectrum(Data):

    """
    This class handles all the data for one spectrum of one detuning for one trial.
    """

    semi_width = 150
    
    def __init__(self, detuning_obj, spectrum_path):
        Data.__init__(self, detuning_obj)
        self.file_path = spectrum_path
        self.frequency = self.detuning_obj.frequency

    def set_S21_has_valid_peak(self):
        peak = np.max(self.S21)
        noise = np.median(self.S21)
        peak_ratio = peak / noise
        self.S21_has_valid_peak = (peak_ratio > self.peak_ratio_threshold)

    def set_S21_centre_frequency(self):
        self.set_S21_centre_frequency_index()

class Transmission(Data):

    """
    This class handles all the data for the transmission of one detuning for one trial.
    """

    semi_width = 15
    
    def __init__(self, detuning_obj, transmission_path):
        Data.__init__(self, detuning_obj)
        self.file_path = transmission_path
        self.set_frequency()

    def set_frequency(self):
        with open(self.file_path, "r") as file:
            file.readline()
            self.frequency = np.array([self.detuning_obj.get_frequency_from_file_line(line)
                                       for line in file])

    def set_S21_has_valid_peak(self):
        self.S21_has_valid_peak = True

    def set_S21_centre_frequency(self):
        self.set_S21_centre_frequency_polynomial_fit(degree=2)

    def remove_S21_discontinuities(self):
        neighbour_averages = self.get_neighbour_averages()
        tolerance = 0.01
        S21_is_good = np.abs(neighbour_averages - self.S21) < tolerance
        self.S21 = self.S21[S21_is_good]
        self.frequency = self.frequency[S21_is_good]

    def get_neighbour_averages(self):
        left = self.S21[:-2]
        right = self.S21[2:]
        neighbour_averages = np.zeros(self.S21.size)
        neighbour_averages[0] = self.S21[0]
        neighbour_averages[-1] = self.S21[-1]
        neighbour_averages[1:-1] = (left + right) / 2
        return neighbour_averages
