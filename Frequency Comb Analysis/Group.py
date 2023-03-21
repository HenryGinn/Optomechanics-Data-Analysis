import os

import numpy as np

from Spectrum import Spectrum
from Utils import get_number_from_file_name

class Group():

    def __init__(self, detuning_obj, path):
        self.detuning_obj = detuning_obj
        self.path = path
        self.set_paths()
        self.set_attributes_initial()

    def set_paths(self):
        self.folder_name = os.path.basename(self.path)
        self.file_names = [file_name for file_name in os.listdir(self.path)]
        self.spectrum_paths = [os.path.join(self.path, file_name)
                               for file_name in self.file_names]

    def set_attributes_initial(self):
        self.drift = self.detuning_obj.drift
        self.group_number = int(self.folder_name[-2])
        self.timestamp = get_number_from_file_name("timestamp", self.file_names[0])

    def create_spectrum_objects(self):
        self.spectrum_objects = [Spectrum(self, path) for path in self.spectrum_paths]

    def process_spectrum(self):
        self.process_spectrum_objects()
        self.frequency = self.spectrum_objects[0].frequency
        self.align_spectra()

    def process_spectrum_objects(self):
        for spectrum_obj in self.spectrum_objects:
            spectrum_obj.set_S21_and_frequency_from_file()
            spectrum_obj.set_peak()

    def align_spectra(self):
        self.set_peak_indexes()
        self.set_max_and_min_peak_indexes()
        self.offset_S21()
        self.offset_frequency()
        self.S21 = np.mean([spectrum_obj.S21_offset for spectrum_obj in self.spectrum_objects], axis=0)

    def set_peak_indexes(self):
        self.peak_indexes = [spectrum_obj.peak_index
                             for spectrum_obj in self.spectrum_objects]

    def set_max_and_min_peak_indexes(self):
        self.max_peak_index = max(self.peak_indexes)
        self.min_peak_index = min(self.peak_indexes)

    def offset_S21(self):
        for spectrum_obj in self.spectrum_objects:
            self.set_S21_offset(spectrum_obj)

    def set_S21_offset(self, spectrum_obj):
        left_index = spectrum_obj.peak_index - self.min_peak_index
        right_index = len(spectrum_obj.S21) - (self.max_peak_index - spectrum_obj.peak_index)
        spectrum_obj.S21_offset = spectrum_obj.S21[left_index:right_index]

    def offset_frequency(self):
        cutoff_size = self.max_peak_index - self.min_peak_index
        frequency_offset_length = len(self.frequency) - cutoff_size
        self.frequency = self.frequency[:frequency_offset_length]
        self.frequency_shift = self.frequency[self.min_peak_index]
        self.frequency -= self.frequency_shift

    def __str__(self):
        string = (f"Detuning: {self.detuning_obj.detuning}\n"
                  f"Group number: {self.group_number}\n"
                  f"Transmission: {self.transmission_path}\n")
        return string
