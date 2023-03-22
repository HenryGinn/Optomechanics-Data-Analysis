import sys
sys.path.append("..")
import os

import numpy as np

from Group import Group
from Utils import make_folder

class Detuning():

    def __init__(self, drift_obj, detuning, paths):
        self.drift_obj = drift_obj
        self.detuning = detuning
        self.paths = paths
        self.process_detuning()

    def process_detuning(self):
        self.drift = self.drift_obj.drift
        self.set_group_objects()
        self.group_size = len(self.group_objects)
        self.set_timestamps()

    def set_group_objects(self):
        self.group_objects = np.array([Group(self, path)
                                       for path in self.paths])

    def set_timestamps(self):
        self.timestamps = [group.timestamp for group in self.group_objects]

    def create_aligned_spectra_folder(self):
        self.aligned_spectra_path = os.path.join(self.drift_obj.aligned_spectra_path,
                                                 f"{self.detuning} dBm")
        make_folder(self.aligned_spectra_path)

    def set_aligned_spectra_paths(self):
        for group_obj in self.group_objects:
            group_obj.set_aligned_spectrum_path()

    def set_aligned_spectra(self):
        for group_obj in self.group_objects:
            group_obj.set_aligned_spectra()

    def load_aligned_spectra(self):
        for group_obj in self.group_objects:
            group_obj.load_aligned_spectrum()

    def set_peak_coordinates_paths(self):
        for group_obj in self.group_objects:
            group_obj.set_peak_coordinates_path()

    def set_peak_coordinates(self):
        print(f"Setting peak coordinates for {self}")
        for group_obj in self.group_objects:
            group_obj.set_peak_coordinates()

    def load_peak_coordinates(self):
        for group_obj in self.group_objects:
            group_obj.load_peak_coordinates()

    def __str__(self):
        string = f"{self.drift_obj}, Detuning {self.detuning}"
        return string
