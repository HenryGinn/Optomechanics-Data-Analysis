import numpy as np
import os
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

    semi_width = 30
    
    def __init__(self, detuning_obj, transmission_path):
        Data.__init__(self, detuning_obj)
        self.file_path = transmission_path
        self.set_frequency()

    def set_frequency(self):
        with open(self.file_path, "r") as file:
            file.readline()
            self.frequency = np.array([self.detuning_obj.get_frequency_from_file_line(line)
                                       for line in file])
class AverageData(Data):

    """
    This class handles the average of data from several files
    """

    def __init__(self, detuning_obj, data_objects, group_indexes):
        Data.__init__(self, detuning_obj)
        self.set_group_information(data_objects, group_indexes)
        self.set_average_S21()

    def set_group_information(self, data_objects, group_indexes):
        self.data_objects = data_objects
        self.group_indexes = group_indexes
        self.group_size = len(group_indexes)

    def set_average_S21(self):
        self.offset_data()
        group_S21_offsets = [data_obj.S21_offset for data_obj in self.data_objects]
        self.S21 = np.mean(group_S21_offsets, axis = 0)

    def offset_data(self):
        self.set_centre_index_data()
        for data_obj in self.data_objects:
            self.set_S21_offset(data_obj)
        self.set_frequency()

    def set_centre_index_data(self):
        self.centre_indexes = [data_obj.S21_centre_index for data_obj in self.data_objects]
        self.min_centre_index = min(self.centre_indexes)
        self.max_centre_index = max(self.centre_indexes)

    def set_S21_offset(self, data_obj):
        left_index = data_obj.S21_centre_index - self.min_centre_index
        right_index = len(data_obj.S21) - (self.max_centre_index - data_obj.S21_centre_index)
        data_obj.S21_offset = data_obj.S21[left_index:right_index]

    def set_frequency(self):
        cutoff_size = self.max_centre_index - self.min_centre_index
        frequency_offset_length = len(self.detuning_obj.frequency) - cutoff_size
        self.frequency = np.copy(self.detuning_obj.frequency[:frequency_offset_length])
        self.frequency -= self.frequency[self.min_centre_index]
    
    def set_gamma(self):
        self.initial_fitting_parameters = self.get_initial_fitting_parameters()
        self.fitting_parameters = self.get_automatic_fit(self.initial_fitting_parameters)
        self.gamma = self.get_gamma_from_fit()

    def output_group(self):
        print("\nOutputting group data")
        print(self)
        for data in self.data_group:
            print(data)

    def __str__(self):
        string = (f"Group size: {self.group_size}\n"
                  f"Group indexes: {self.group_indexes}\n")
        return string
