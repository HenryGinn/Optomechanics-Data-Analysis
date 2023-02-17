from Data import Data
import os
import numpy as np

class Spectrum(Data):

    """
    This class handles all the data for one spectrum of one detuning for one trial.
    """

    semi_width = 150
    
    def __init__(self, detuning_obj, spectrum_path):
        Data.__init__(self, detuning_obj, spectrum_path)
        self.frequency = self.detuning_obj.frequency

    def is_spectrum_valid(self):
        return True

class Transmission(Data):

    """
    This class handles all the data for the transmission of one detuning for one trial.
    """

    semi_width = 30
    
    def __init__(self, detuning_obj, transmission_path):
        Data.__init__(self, detuning_obj, transmission_path)
        self.set_frequency()

    def set_frequency(self):
        with open(self.file_path, "r") as file:
            file.readline()
            self.frequency = np.array([self.detuning_obj.get_frequency_from_file_line(line)
                                       for line in file])
