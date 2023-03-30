import numpy as np

from Utils import get_sliced_list
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Plotting.PlotUtils import get_group_size
from Plotting.PlotUtils import get_group_indexes

class PlotSpectra():

    name = "Plot Spectra"
    noise = False
    markers = False
    fit = False

    def __init__(self, data_set_obj):
        self.data_set_obj = data_set_obj

    def plot(self, **kwargs):
        self.kwargs = kwargs
        self.data_set_obj.average_groups("Load")
        self.process_kwargs()
        for drift_obj in self.data_set_obj.drift_objects:
            self.plot_drift_objects(drift_obj)

    def process_kwargs(self):
        self.process_noise()
        self.process_markers()
        self.process_fit()

    def process_noise(self):
        if "noise" in self.kwargs:
            self.noise = self.kwargs["noise"]
        if self.noise:
            self.data_set_obj.noise_threshold("Load")

    def process_markers(self):
        if "markers" in self.kwargs:
            self.markers = self.kwargs["markers"]
        if self.markers:
            self.data_set_obj.peak_coordinates("Load")

    def process_fit(self):
        if "fit" in self.kwargs:
            self.fit = self.kwargs["fit"]
        if self.fit:
            self.data_set_obj.envelope_vertices("Load")

    def plot_drift_objects(self, drift_obj):
        detuning_lines_objects = self.get_detuning_lines_objects(drift_obj)
        title = f"{drift_obj} Frequency Comb"
        self.create_plots(detuning_lines_objects, title)

    def get_detuning_lines_objects(self, drift_obj):
        lines_objects = [self.get_detuning_lines_obj(detuning_obj)
                         for detuning_obj in drift_obj.detuning_objects]
        return lines_objects

    def get_detuning_lines_obj(self, detuning_obj):
        lines_obj = self.create_lines_obj(detuning_obj)
        self.set_lines_labels(lines_obj, detuning_obj)
        return lines_obj

    def create_lines_obj(self, detuning_obj):
        line_objects = self.get_line_objects(detuning_obj)
        lines_obj = Lines(line_objects, plot_type="semilogy")
        return lines_obj

    def get_line_objects(self, detuning_obj):
        line_objects = [self.get_line_object(detuning_obj)]
        line_objects = self.add_peak_attributes(detuning_obj, line_objects)
        return line_objects

    def get_line_object(self, detuning_obj):
        x_values = detuning_obj.spectrum_obj.frequency
        y_values = detuning_obj.spectrum_obj.S21
        line_obj = Line(x_values, y_values)
        return line_obj

    def add_peak_attributes(self, detuning_obj, line_objects):
        line_objects = self.add_noise(detuning_obj, line_objects)
        line_objects = self.add_markers(detuning_obj, line_objects)
        line_objects = self.add_fit(detuning_obj, line_objects)
        return line_objects

    def add_noise(self, detuning_obj, line_objects):
        if self.noise:
            line_objects.append(self.get_line_object_noise(detuning_obj.spectrum_obj))
        return line_objects

    def get_line_object_noise(self, spectrum_obj):
        x_values = spectrum_obj.frequency
        y_values = spectrum_obj.noise_threshold
        line_obj = Line(x_values, y_values, colour="k")
        return line_obj

    def add_markers(self, detuning_obj, line_objects):
        if self.markers:
            line_objects.append(self.get_line_object_marker(detuning_obj))
        return line_objects

    def get_line_object_marker(self, detuning_obj):
        x_values = detuning_obj.spectrum_obj.peak_frequencies
        y_values = detuning_obj.spectrum_obj.peak_S21s
        line_obj = Line(x_values, y_values, colour="r", marker="*", linestyle="None")
        return line_obj

    def add_fit(self, detuning_obj, line_objects):
        if self.fit:
            line_objects.append(self.get_line_obj_fit(detuning_obj))
        return line_objects

    def get_line_obj_fit(self, detuning_obj):
        x_values = detuning_obj.envelope_x_values
        y_values = detuning_obj.envelope_y_values
        line_obj = Line(x_values, y_values, colour="k")
        return line_obj

    def set_lines_labels(self, lines_obj, detuning_obj):
        lines_obj.title = f"Detuning: {detuning_obj.detuning} Hz"
        lines_obj.x_label = "Frequency (Hz)"
        lines_obj.y_label = "S21 (mW)"

    def create_plots(self, lines_objects, title):
        plot_obj = Plots(lines_objects, self.kwargs)
        plot_obj.title = title
        plot_obj.plot()
