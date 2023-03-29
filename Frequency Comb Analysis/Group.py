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
