import os

import numpy as np

from Spectrum import Spectrum
from FitPeaks import FitPeaks
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
        self.detuning = self.detuning_obj.detuning
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

    def save_peak_coordinates(self):
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

    def fit_peaks(self):
        self.peaks_fit_obj = FitPeaks(self)
        self.peaks_fit_obj.spectrum_obj = self.spectrum_obj
        self.peaks_fit_obj.set_peak_data()
        self.peaks_fit_obj.fit_peaks()

    def save_peak_lines_to_file(self, file):
        self.write_group_data_to_file(file)
        self.write_line_data_to_file(file)

    def write_group_data_to_file(self, file):
        detuning = self.detuning_obj.detuning
        group = self.group_number
        file.writelines(f"{detuning}\t{group}\t")

    def write_line_data_to_file(self, file):
        gradient = self.peaks_fit_obj.fitting_parameters[0]
        intercept = self.peaks_fit_obj.fitting_parameters[1]
        file.writelines(f"{gradient}\t{intercept}\n")

    def set_envolope_values(self):
        if hasattr(self, "spectrum_obj"):
            self.peaks_fit_obj.set_envelope_values()
            self.envelope_x_values = self.peaks_fit_obj.envelope_x_values
            self.envelope_y_values = self.peaks_fit_obj.envelope_y_values
        
    def __str__(self):
        string = (f"Detuning: {self.detuning_obj.detuning}\n"
                  f"Group number: {self.group_number}\n"
                  f"Transmission: {self.transmission_path}\n")
        return string
