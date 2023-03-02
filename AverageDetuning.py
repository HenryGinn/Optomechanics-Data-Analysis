import numpy as np
import math
from AverageData import AverageData
import Utils

class AverageDetuning():

    def __init__(self, detuning_obj):
        self.detuning = detuning_obj
    
    def set_S21_average_objects(self, average_size):
        average_size = self.get_average_size(average_size, len(self.detuning.spectrum_objects_valid))
        group_indexes_all = self.get_group_indexes(len(self.detuning.spectrum_indexes), average_size)
        self.S21_average_objects = [self.get_S21_average_obj(group_indexes)
                                    for group_indexes in group_indexes_all]

    def get_S21_average_obj(self, group_indexes):
        spectrum_indexes = self.detuning.spectrum_indexes[group_indexes]
        S21_group = [self.detuning.spectrum_objects_valid[index] for index in group_indexes]
        S21_average_obj = AverageData(self.detuning, S21_group, spectrum_indexes)
        return S21_average_obj
    
    def get_average_size(self, average_size, total_count):
        if average_size is None:
            average_size = total_count
        return average_size

    def average_list(self, list_full, average_size):
        group_indexes = self.get_group_indexes(len(list_full), average_size)
        list_averages = [np.mean(list_full[indexes], axis = 0)
                         for indexes in group_indexes]
        return list_averages
    
    def get_group_indexes(self, length, group_size):
        group_size, group_count = self.get_group_data(length, group_size)
        end_point_indexes = self.get_end_point_indexes(length, group_size, group_count)
        group_indexes = [np.arange(end_point_indexes[group_number],
                                   end_point_indexes[group_number + 1]).astype('int')
                         for group_number in range(group_count)]
        return group_indexes

    def get_group_data(self, length, group_size):
        group_size = self.get_modified_group_size(length, group_size)
        group_count = math.floor(length/group_size)
        return group_size, group_count

    def get_modified_group_size(self, list_size, average_size):
        if list_size < average_size:
            average_size = list_size
        return average_size

    def get_end_point_indexes(self, length, group_size, group_count):
        real_group_size = length/group_count
        real_group_end_points = np.arange(0, group_count + 1) * real_group_size
        real_group_end_points = np.round(real_group_end_points, 5)
        end_point_indexes = np.ceil(real_group_end_points)
        return end_point_indexes

    def get_drifts(self, indexes, total):
        if hasattr(self.detuning.transmission, 'S21_centre_frequency'):
            return self.do_get_drifts(indexes, total)
        else:
            raise Exception(("Interpolation requires information about the transmission\n"
                             "Run the process_transmission method first"))

    def do_get_drifts(self, indexes, total):
        spacings = indexes / total
        current_detuning = self.detuning.transmission.S21_centre_frequency
        #print(self.detuning)
        #print(self.detuning.next_detuning)
        next_detuning = self.detuning.next_detuning.transmission.S21_centre_frequency
        difference = next_detuning - current_detuning
        drifts = difference*spacings
        return drifts

    def set_drifts_average(self, average_obj):
        indexes = average_obj.group_indexes
        spectra_count = len(self.detuning.spectrum_objects)
        drifts = self.get_drifts(indexes, spectra_count)
        average_obj.drift = np.mean(drifts)

    def get_standard_deviations(self, list_full, average_size):
        group_indexes = self.get_group_indexes(len(list_full), average_size)
        standard_deviations = [np.std(list_full[indexes])
                                      for indexes in group_indexes]
        return standard_deviations
