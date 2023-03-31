import os

import numpy as np

from CombFunction import CombFunction
from PeakFits import evaluate_abs
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path

class PeakGaps(CombFunction):

    name = "Peak Gaps"

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
        drift_obj.peak_gaps_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.drift_obj.peak_gaps_path,
                            f"{detuning_obj.detuning} Hz")
        detuning_obj.peak_gaps_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.peak_coordinates("Load")

    def save_data_set_obj(self, data_set_obj):
        for drift_obj in data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.set_peak_gaps(detuning_obj)
            self.save_peak_gaps(detuning_obj)

    def set_peak_gaps(self, detuning_obj):
        frequencies = detuning_obj.spectrum_obj.peak_frequencies
        peak_gaps = [frequencies[index + 1] - frequencies[index]
                     for index in range(len(frequencies) - 1)]
        detuning_obj.peak_gaps = peak_gaps
    
    def save_peak_gaps(self, detuning_obj):
        with open(detuning_obj.peak_gaps_path, "w") as file:
            file.writelines("Gap number\tFrequency (Hz)\n")
            self.save_peak_gaps_to_file(detuning_obj, file)
    
    def save_peak_gaps_to_file(self, detuning_obj, file):
        for index, gap in enumerate(detuning_obj.peak_gaps):
            file.writelines(f"{index}\t{gap}\n")
    
    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.peak_gaps_path)
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects])

    def do_load_data(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.load_drift_obj(drift_obj)

    def load_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.load_detuning_obj(detuning_obj)

    def load_detuning_obj(self, detuning_obj):
        file_contents = get_file_contents_from_path(detuning_obj.peak_gaps_path)
        _, detuning_obj.peak_gaps = file_contents

    def get_lines_objects(self):
        lines_objects = [self.get_lines_obj(drift_obj)
                         for drift_obj in self.data_set_obj.drift_objects]
        return lines_objects

    def get_lines_obj(self, drift_obj):
        line_objects = [self.get_line_obj(detuning_obj)
                        for detuning_obj in drift_obj.detuning_objects]
        lines_obj = Lines(line_objects)
        lines_obj.title = f"{drift_obj.drift_value} dBm"
        self.set_labels(lines_obj)
        return lines_obj

    def get_line_obj(self, detuning_obj):
        label = detuning_obj.detuning
        x_values = np.arange(len(detuning_obj.peak_gaps)) + 1
        y_values = detuning_obj.peak_gaps
        line_obj = Line(x_values, y_values, label=label)
        return line_obj

    def set_labels(self, lines_obj):
        lines_obj.x_label = "Gap Number"
        lines_obj.y_label = "Gap Size (Hz)"
        lines_obj.set_rainbow_lines(value=0.9)

    def create_plots(self, lines_objects, title, kwargs):
        plots_obj = Plots(lines_objects, kwargs, universal_legend=True)
        plots_obj.parent_results_path = self.folder_path
        plots_obj.title = title
        plots_obj.plot()
