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

    def is_spectrum_valid(self):
        return True

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

    def remove_S21_discontinuities(self):
        neighbour_averages = self.get_neighbour_averages()
        tolerance = 0.01
        S21_is_bad = np.abs(neighbour_averages - self.S21) > tolerance
        self.S21 = np.where(S21_is_bad, neighbour_averages, self.S21)

    def get_neighbour_averages(self):
        left = self.S21[:-2]
        right = self.S21[2:]
        neighbour_averages = np.zeros(self.S21.size)
        neighbour_averages[0] = self.S21[0]
        neighbour_averages[-1] = self.S21[-1]
        neighbour_averages[1:-1] = (left + right) / 2
        return neighbour_averages
