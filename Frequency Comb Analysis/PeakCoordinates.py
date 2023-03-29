import os

import numpy as np

from CombFunction import CombFunction
from Utils import make_folder

class PeakCoordinates(CombFunction):

    name = "Peak Coordinates"

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        self.set_folder_path()
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)
            self.set_detuning_paths(drift_obj)

    def set_drift_path(self, drift_obj):
        path = os.path.join(self.folder_path, drift_obj.folder_name)
        drift_obj.peak_coordinates_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            path = os.path.join(drift_obj.peak_coordinates_path,
                                f"{detuning_obj.detuning} Hz")
            detuning_obj.peak_coordinates_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.align_spectra("Load")
        self.data_set_obj.average_groups("Load")
        self.data_set_obj.noise_threshold("Load")

    def save_data_set_obj(self, data_set_obj):
        for drift_obj in self.data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.save_detuning_obj(detuning_obj)

    def save_detuning_obj(self, detuning_obj):
        pass

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.peak_coordinates_path)
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects])

    def do_load_data(self):
        pass
