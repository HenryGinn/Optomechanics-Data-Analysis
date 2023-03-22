import os

import numpy as np

from Spectrum import Spectrum
from Utils import get_number_from_file_name
from Utils import get_file_contents_from_path

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
        self.spectrum_objects = [self.get_spectrum_obj(path)
                                 for path in self.spectrum_paths]

    def get_spectrum_obj(self, path):
        spectrum_obj = Spectrum(self)
        spectrum_obj.initialise_from_path(path)
        return spectrum_obj

    def set_aligned_spectrum_path(self):
        self.aligned_spectrum_path = os.path.join(self.detuning_obj.aligned_spectra_path,
                                                  f"Group {self.group_number}")

    def set_aligned_spectra(self):
        self.process_spectrum_objects()
        self.spectrum_obj = Spectrum(self)
        self.spectrum_obj.frequency = self.spectrum_objects[0].frequency
        self.align_spectra()
        self.create_aligned_spectrum_file()

    def process_spectrum_objects(self):
        for spectrum_obj in self.spectrum_objects:
            spectrum_obj.set_S21_and_frequency_from_file()
            spectrum_obj.set_peak()

    def align_spectra(self):
        self.set_peak_indexes()
        self.set_max_and_min_peak_indexes()
        self.offset_S21()
        self.offset_frequency()
        self.spectrum_obj.S21 = np.mean([spectrum_obj.S21_offset for spectrum_obj in self.spectrum_objects], axis=0)

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
        frequency_offset_length = len(self.spectrum_obj.frequency) - cutoff_size
        self.spectrum_obj.frequency = self.spectrum_obj.frequency[:frequency_offset_length]
        frequency_shift = self.spectrum_obj.frequency[self.min_peak_index]
        self.spectrum_obj.frequency -= frequency_shift

    def create_aligned_spectrum_file(self):
        with open(self.aligned_spectrum_path, "w") as file:
            file.writelines("S21 (mW)\tFrequency (Hz)\n")
            self.save_aligned_spectrum(file)

    def save_aligned_spectrum(self, file):
        for S21, frequency in zip(self.spectrum_obj.S21,
                                  self.spectrum_obj.frequency):
            file.writelines(f"{S21}\t{frequency}\n")

    def load_aligned_spectrum(self):
        self.create_blank_spectrum_obj()
        file_contents = get_file_contents_from_path(self.aligned_spectrum_path)
        self.spectrum_obj.S21, self.spectrum_obj.frequency = file_contents

    def create_blank_spectrum_obj(self):
        if not hasattr(self, "spectrum_obj"):
            self.spectrum_obj = Spectrum(self)

    def set_peak_coordinates(self):
        self.spectrum_obj.set_peak_coordinates()
        self.create_peak_coordinates_file()

    def create_peak_coordinates_file(self):
        with open(self.peak_coordinates_path, "w") as file:
            file.writelines("Index\tFrequency (Hz)\tS21 (mW)\n")
            self.save_peak_coordinates_to_file(file)

    def set_peak_coordinates_path(self):
        detuning = self.detuning_obj.detuning
        file_name = f"Detuning_{detuning}_Group_{self.group_number}.txt"
        base_path = self.detuning_obj.drift_obj.peak_coordinates_path
        self.peak_coordinates_path = os.path.join(base_path, file_name)

    def save_peak_coordinates_to_file(self, file):
        for peak_index in self.spectrum_obj.peak_indices:
            frequency = self.spectrum_obj.frequency[peak_index]
            S21 = self.spectrum_obj.S21[peak_index]
            file.writelines(f"{peak_index}\t{frequency}\t{S21}\n")

    def load_peak_coordinates(self):
        self.create_blank_spectrum_obj()
        path = self.peak_coordinates_path
        file_contents = get_file_contents_from_path(path)
        self.set_peak_coordinates_from_file_contents(file_contents)

    def set_peak_coordinates_from_file_contents(self, file_contents):
        (self.spectrum_obj.peak_indices,
         self.spectrum_obj.peak_frequencies,
         self.spectrum_obj.peak_S21s) = file_contents

    def __str__(self):
        string = (f"Detuning: {self.detuning_obj.detuning}\n"
                  f"Group number: {self.group_number}\n"
                  f"Transmission: {self.transmission_path}\n")
        return string
