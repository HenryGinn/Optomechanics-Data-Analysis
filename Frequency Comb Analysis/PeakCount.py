import os

import numpy as np

from CombFunction import CombFunction
from PeakFits import evaluate_abs
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path

class PeakCount(CombFunction):

    name = "Peak Count"

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        self.set_folder_path()
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)

    def set_drift_path(self, drift_obj):
        path = os.path.join(self.folder_path, f"{drift_obj.folder_name}")
        drift_obj.peak_count_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.peak_coordinates("Load")

    def save_data_set_obj(self, data_set_obj):
        for drift_obj in data_set_obj.drift_objects:
            self.set_peak_count(drift_obj)
            self.save_peak_count(drift_obj)

    def set_peak_count(self, drift_obj):
        drift_obj.peak_counts = [len(detuning_obj.spectrum_obj.peak_indices)
                                 for detuning_obj in drift_obj.detuning_objects]
    
    def save_peak_count(self, drift_obj):
        with open(drift_obj.peak_count_path, "w") as file:
            file.writelines("Detuning (Hz)\tCount\n")
            self.save_peak_count_to_file(drift_obj, file)
    
    def save_peak_count_to_file(self, drift_obj, file):
        for detuning_obj, count in zip(drift_obj.detuning_objects, drift_obj.peak_counts):
            detuning = detuning_obj.detuning
            file.writelines(f"{detuning}\t{count}\n")
    
    def data_is_saved(self):
        return np.all([os.path.exists(drift_obj.peak_count_path)
                       for drift_obj in self.data_set_obj.drift_objects])

    def do_load_data(self):
        for drift_obj in self.data_set_obj.drift_objects:
            file_contents = get_file_contents_from_path(drift_obj.peak_count_path)
            _, drift_obj.peak_counts = file_contents

    def get_lines_objects(self):
        line_objects = [self.get_line_obj(drift_obj)
                        for drift_obj in self.data_set_obj.drift_objects]
        lines_obj = Lines(line_objects, legend=True, legend_loc="lower right")
        self.set_labels(lines_obj)
        return [lines_obj]

    def get_line_obj(self, drift_obj):
        label = f"{drift_obj.drift_value} dBm"
        x_values = [detuning_obj.detuning for detuning_obj in drift_obj.detuning_objects]
        y_values = drift_obj.peak_counts
        line_obj = Line(x_values, y_values, label=label)
        return line_obj

    def set_labels(self, lines_obj):
        lines_obj.x_label = "Detuning (Hz)"
        lines_obj.y_label = "Number of Peaks"
        lines_obj.set_rainbow_lines(value=0.9)

    def create_plots(self, lines_objects, title, kwargs):
        plots_obj = Plots(lines_objects, kwargs)
        plots_obj.parent_results_path = self.folder_path
        plots_obj.title = title
        plots_obj.plot()
