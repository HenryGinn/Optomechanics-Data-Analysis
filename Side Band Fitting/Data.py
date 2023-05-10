import os
import numpy as np
import scipy as sc
import math
from Utils import get_file_contents_from_path
from Utils import evaluate_lorentzian

class Data():

    """
    This class handles all the data for S21 and frequency pair.
    This could be a spectrum, a transmission, or an average of several spectra.

    Spectrum and Transmission are subclasses of this.
    """

    frequency_shift = 0
    semi_width = 150
    review_centre_heuristic_plot = False
    review_centre_results_plot = False
    suppress_centre_computation_warnings = True
    
    def __init__(self, detuning_obj):
        self.detuning_obj = detuning_obj
        self.detuning = detuning_obj.detuning
        self.power = self.detuning_obj.trial_obj.power
        self.timestamp = self.detuning_obj.timestamp

    def process_S21(self):
        if self.S21_has_valid_peak:
            self.set_peak_index()

    def load_S21(self):
        file_contents = get_file_contents_from_path(self.file_path)
        voltage, self.frequency = file_contents
        self.set_S21_from_voltage(voltage)

    def set_S21_from_voltage(self, voltage):
        cable_attenuation = 0
        self.S21 = (10**((voltage + cable_attenuation)/10))/1000

    def set_peak_index(self):
        if self.if_large_peak():
            self.set_peak_index_large()
        else:
            self.set_peak_index_small()

    
    def get_peak_index(self):
        if self.S21_has_valid_peak:
            return self.peak_index
        else:
            return None

    def get_peak_frequency(self):
        if self.S21_has_valid_peak:
            return self.peak_frequency
        else:
            return None

    def set_amplitude_from_fit(self):
        function_values = evaluate_lorentzian(self.frequency, self.fitting_parameters)
        self.amplitude = max(function_values)

    def set_omega_from_fit(self):
        centre_frequency = self.fitting_parameters[3] + self.frequency_shift
        self.omega = centre_frequency - self.detuning_obj.cavity_frequency - self.detuning_obj.detuning
    
    def __str__(self):
        string = (f"Detuning: {self.detuning}\n"
                  f"Power: {self.power}\n"
                  f"Timestamp: {self.timestamp}\n"
                  f"File path: {self.file_path}\n")
        return string
