import os

import numpy as np
import scipy.fft as fft
import matplotlib.pyplot as plt

from CombFunction import CombFunction
from PeakFits import evaluate_abs
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path

class ReverseFourierTransform(CombFunction):

    name = "Reverse Fourier Transform"
    resolution = 30000

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
        drift_obj.reverse_fourier_transform_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.drift_obj.reverse_fourier_transform_path,
                            f"{detuning_obj.detuning} Hz")
        detuning_obj.reverse_fourier_transform_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.spectra_peaks("Load")
        self.data_set_obj.peak_coordinates("Load")

    def save_data_set_obj(self, data_set_obj):
        for drift_obj in data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.set_reverse_fourier_transform(detuning_obj)
            self.save_reverse_fourier_transform(detuning_obj)

    def set_reverse_fourier_transform(self, detuning_obj):
        offset_frequency = self.get_offset_frequency(detuning_obj)
        peak_frequencies = detuning_obj.spectrum_obj.peak_frequencies + offset_frequency
        peak_S21s = detuning_obj.spectrum_obj.peak_S21s
        detuning_obj.fourier_x = np.linspace(0, 0.0001, self.resolution + 1)
        time_mesh = np.outer(peak_frequencies, detuning_obj.fourier_x)
        detuning_obj.fourier_y = np.dot(peak_S21s, np.sin(time_mesh))

    def get_offset_frequency(self, detuning_obj):
        offset_frequencies = [spectrum_obj.peak_frequency
                              for group_obj in detuning_obj.group_objects
                              for spectrum_obj in group_obj.spectrum_objects]
        offset_frequency = np.mean(offset_frequencies)
        return offset_frequency
    
    def save_reverse_fourier_transform(self, detuning_obj):
        with open(detuning_obj.reverse_fourier_transform_path, "w") as file:
            file.writelines("Time (s)\tValue\n")
            self.save_reverse_fourier_transform_to_file(detuning_obj, file)
    
    def save_reverse_fourier_transform_to_file(self, detuning_obj, file):
        x_values = detuning_obj.fourier_x
        y_values = detuning_obj.fourier_y
        for x_value, y_value in zip(x_values, y_values):
            file.writelines(f"{x_value}\t{y_value}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.reverse_fourier_transform_path)
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects])

    def do_load_data(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.load_drift_obj(drift_obj)

    def load_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.load_detuning_obj(detuning_obj)

    def load_detuning_obj(self, detuning_obj):
        file_contents = get_file_contents_from_path(detuning_obj.reverse_fourier_transform_path)
        detuning_obj.fourier_x = file_contents[0]
        detuning_obj.fourier_y = file_contents[1]

    def plot(self, **kwargs):
        self.process_args(**kwargs)
        lines_objects = self.get_lines_objects()
        title = f"{self.data_set_obj} {self.name}\n "
        self.create_plots(lines_objects, title, kwargs)

    def process_args(self, **kwargs):
        self.process_resolution(**kwargs)
        self.process_subplots(**kwargs)
        self.process_aspect_ratio(**kwargs)

    def process_resolution(self, **kwargs):
        if "resolution" in kwargs:
            self.resolution = kwargs["resolution"]
        self.ensure_resolution_matches()

    def ensure_resolution_matches(self):
        if not self.resolution_matches():
            self.execute("Save")

    def resolution_matches(self):
        return np.all([len(detuning_obj.fourier_x) == self.resolution + 1
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects])

    def process_subplots(self, **kwargs):
        if "subplots" in kwargs:
            self.subplots = kwargs["subplots"]
        else:
            self.subplots = None

    def process_aspect_ratio(self, **kwargs):
        if "aspect_ratio" in kwargs:
            self.aspect_ratio = kwargs["aspect_ratio"]
        else:
            self.aspect_ratio = None

    def get_lines_objects(self):
        lines_objects = [self.get_lines_obj(drift_obj)
                         for drift_obj in self.data_set_obj.drift_objects]
        return lines_objects

    def get_lines_obj(self, drift_obj):
        line_objects = [self.get_line_obj(detuning_obj)
                        for detuning_obj in drift_obj.detuning_objects]
        lines_obj = Lines(line_objects, plot_type="plot")
        lines_obj.title = f"{drift_obj.drift_value} dBm"
        self.set_labels(lines_obj)
        return lines_obj

    def get_line_obj(self, detuning_obj):
        label = detuning_obj.detuning
        x_values = detuning_obj.fourier_x
        y_values = detuning_obj.fourier_y
        line_obj = Line(x_values, y_values, label=label)
        line_obj.label_units = "Hz"
        return line_obj

    def set_labels(self, lines_obj):
        self.set_x_labels(lines_obj)
        self.set_y_labels(lines_obj)
        lines_obj.set_rainbow_lines(value=0.9)

    def set_x_labels(self, lines_obj):
        lines_obj.x_label = "Time"
        lines_obj.x_units = "s"
        lines_obj.x_label_type = "Prefix"

    def set_y_labels(self, lines_obj):
        lines_obj.y_label = None
        lines_obj.y_units = ""
        lines_obj.y_label_type = "Count"

    def create_plots(self, lines_objects, title, kwargs):
        plots_obj = Plots(lines_objects, kwargs)
        plots_obj.parent_results_path = self.folder_path
        plots_obj.title = title
        plots_obj.plot()
