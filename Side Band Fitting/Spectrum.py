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

    def set_S21_has_valid_peak(self):
        peak = np.max(self.S21)
        noise = np.median(self.S21)
        peak_ratio = peak / noise
        self.S21_has_valid_peak = (peak_ratio > self.peak_ratio_threshold)

    def set_S21_centre_frequency(self):
        self.set_S21_centre_frequency_peak()
