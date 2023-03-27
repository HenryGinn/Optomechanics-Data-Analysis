import os

import numpy as np

from CombFunction import CombFunction
from Utils import make_folder

class PeakGaps(CombFunction):

    name = "Peak Gaps"

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def save_data(self):
        print(f"Saving '{self.name}' Data")
        self.set_paths()

    def set_paths(self):
        self.set_folder_path()
        self.set_file_path()

    def set_file_path(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)
            self.set_detuning_paths(drift_obj)

    def set_drift_path(self, drift_obj):
        path = os.path.join(self.folder_path, drift_obj.folder_name)
        drift_obj.peak_gaps_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            path = os.path.join(drift_obj.peak_gaps_path, f"{detuning_obj.detuning} Hz")
            detuning_obj.peak_gaps_path = path

    def load_data(self):
        self.set_paths()
        if self.data_is_saved():
            self.do_load_data()
        else:
            self.execute("Save")

    def do_load_data(self):
        print(f"Loading '{self.name}' Data")

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.average_group_path)
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects])
    
    def create_plot(self):
        self.ensure_data_is_loaded()
