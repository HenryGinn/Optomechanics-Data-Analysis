import os

import numpy as np

from CombFunction import CombFunction

class PeakFits(CombFunction):

    name = "Peak Fits"

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        self.set_folder_path()
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)

    def set_drift_path(self, drift_obj):
        drift_obj.peak_fits_path = os.path.join(self.folder_path,
                                                f"{drift_obj.folder_name}.txt")

    def data_is_saved(self):
        return np.all([os.path.exists(drift_obj.peak_fits_path)
                       for drift_obj in self.data_set_obj.drift_objects])

    def save_data(self):
        print(f"Saving '{self.name}' Data")
        self.set_paths()
        for drift_obj in self.data_set_obj.drift_objects:
            for detuning_obj in drift_obj.detuning_objects:
                self.save_data_detuning(detuning_obj)

    def save_data_detuning(self, detuning_obj):
        print(detuning_obj.spectrum_obj)

    def do_load_data(self):
        pass
