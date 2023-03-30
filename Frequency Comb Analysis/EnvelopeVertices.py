import os

import numpy as np

from CombFunction import CombFunction
from PeakFits import evaluate_abs
from Utils import make_folder
from Utils import get_file_contents_from_path

class EnvelopeVertices(CombFunction):

    name = "Envelope Vertices"

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        self.set_folder_path()
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)
            self.set_detuning_paths(drift_obj)

    def set_drift_path(self, drift_obj):
        path = os.path.join(self.folder_path, f"{drift_obj.folder_name}")
        drift_obj.envelope_vertices_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.drift_obj.envelope_vertices_path,
                            f"{detuning_obj.detuning} Hz")
        detuning_obj.envelope_vertices_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.peak_coordinates("Load")
        self.data_set_obj.peak_fits("Load")

    def save_data_set_obj(self, data_set_obj):
        for drift_obj in data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.set_envelope_vertices(detuning_obj)
            self.save_envelope_vertices(detuning_obj)

    def set_envelope_vertices(self, detuning_obj):
        self.set_envelope_x_values(detuning_obj)
        self.set_envelope_y_values(detuning_obj)

    def set_envelope_x_values(self, detuning_obj):
        left_x = detuning_obj.spectrum_obj.peak_frequencies[0]
        right_x = detuning_obj.spectrum_obj.peak_frequencies[-1]
        detuning_obj.envelope_x_values = np.array([left_x, 0, right_x])

    def set_envelope_y_values(self, detuning_obj):
        detuning_obj.envelope_y_values = evaluate_abs(detuning_obj.envelope_x_values,
                                                      detuning_obj.fitting_parameters)
        detuning_obj.envelope_y_values = np.exp(detuning_obj.envelope_y_values)

    def save_envelope_vertices(self, detuning_obj):
        with open(detuning_obj.envelope_vertices_path, "w") as file:
            file.writelines("X Values (Hz)\tY Values (S21)\n")
            self.save_envelope_vertices_to_file(detuning_obj, file)
    
    def save_envelope_vertices_to_file(self, detuning_obj, file):
        x_values = detuning_obj.envelope_x_values
        y_values = detuning_obj.envelope_y_values
        for x_value, y_value in zip(x_values, y_values):
            file.writelines(f"{x_value}\t{y_value}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.envelope_vertices_path)
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects])

    def do_load_data(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.load_drift_obj(drift_obj)

    def load_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.load_detuning_obj(detuning_obj)

    def load_detuning_obj(self, detuning_obj):
        file_contents = get_file_contents_from_path(detuning_obj.envelope_vertices_path)
        detuning_obj.envelope_x_values, detuning_obj.envelope_y_values = file_contents
