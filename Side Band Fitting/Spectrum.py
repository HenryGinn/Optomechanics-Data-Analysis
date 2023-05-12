import numpy as np

from Data import Data

class Spectrum(Data):

    """
    This class handles all the data for one spectrum of one detuning for one trial.
    """
    
    def __init__(self, detuning_obj, spectrum_path):
        Data.__init__(self, detuning_obj)
        self.file_path = spectrum_path
        self.frequency = self.detuning_obj.frequency
        self.index = detuning_obj.spectrum_paths.index(spectrum_path)
        self.set_moving_average_size()

    def set_moving_average_size(self):
        moving_average = {-20: 20, -19: 20, -18: 20, -17: 20, -16: 20, -15: 20,
                          -14: 20, -13: 20, -12: 20, -11: 20, -10: 20, -9: 20,
                          -8: 20, -7: 20, -6: 20, -5: 20, -4: 20, -3: 20, -2: 1,
                          -1: 1, 0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1,
                          8: 1, 9: 1, 10: 1, 11: 4, 12: 4, 13: 20, 14: 20, 15: 20,
                          16: 20, 17: 20, 18: 20, 19: 20}
        key = int(self.detuning_obj.detuning / 10**6)
        self.moving_average_size = moving_average[key]

    def set_S21_has_valid_peak(self):
        peak = np.max(self.S21)
        noise = np.median(self.S21)
        peak_ratio = peak / noise
        self.S21_has_valid_peak = (peak_ratio > self.peak_ratio_threshold)

    def set_S21_centre_frequency(self):
        self.set_S21_centre_frequency_peak()

    def __str__(self):
        string = f"{self.detuning_obj}, Spectrum {self.index}"
        return string
