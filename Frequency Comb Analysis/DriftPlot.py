import numpy as np

from Utils import get_sliced_list
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Plotting.PlotUtils import get_group_size
from Plotting.PlotUtils import get_group_indexes

class DriftPlot():

    def __init__(self, drift_obj, subplots):
        self.drift_obj = drift_obj
        self.subplots = subplots

    def plot_spectra(self):
        detuning_lines_objects = self.get_detuning_lines_objects()
        title = f"{self.drift_obj} Frequency Comb"
        self.create_plots(detuning_lines_objects, title)

    def set_data_plotting_instructions(self, detunings, groups):
        self.detunings = detunings
        self.groups = groups

    def set_peak_plotting_instructions(self, noise, markers, fit):
        self.noise = noise
        self.markers = markers
        self.fit = fit

    def get_detuning_lines_objects(self):
        detuning_objects = get_sliced_list(self.drift_obj.detuning_objects,
                                           self.detunings)
        lines_objects = [self.get_detuning_lines_obj(detuning_obj)
                         for detuning_obj in detuning_objects]
        return lines_objects

    def get_detuning_lines_obj(self, detuning_obj):
        lines_obj = self.create_lines_obj(detuning_obj)
        self.set_lines_labels(lines_obj, detuning_obj)
        return lines_obj

    def create_lines_obj(self, detuning_obj):
        line_objects = self.get_line_objects(detuning_obj)
        lines_obj = Lines(line_objects)
        return lines_obj

    def get_line_objects(self, detuning_obj):
        group_objects = get_sliced_list(detuning_obj.group_objects, self.groups)
        line_objects = self.get_lines(group_objects)
        line_objects = self.add_peak_attributes(group_objects, line_objects)
        return line_objects

    def get_lines(self, group_objects):
        line_objects = [self.get_line_object(group_obj)
                        for group_obj in group_objects]
        return line_objects

    def get_line_object(self, group_obj):
        x_values = group_obj.spectrum_obj.frequency
        y_values = group_obj.spectrum_obj.S21
        line_obj = Line(x_values, y_values)
        return line_obj

    def add_peak_attributes(self, group_objects, line_objects):
        line_objects = self.add_noise(group_objects, line_objects)
        line_objects = self.add_markers(group_objects, line_objects)
        line_objects = self.add_fit(group_objects, line_objects)
        return line_objects

    def add_noise(self, group_objects, line_objects):
        if self.noise:
            for group_obj in group_objects:
                line_objects.append(self.get_line_object_noise(group_obj.spectrum_obj))
        return line_objects

    def get_line_object_noise(self, spectrum_obj):
        x_values = spectrum_obj.frequency
        y_values = spectrum_obj.noise_threshold
        line_obj = Line(x_values, y_values, colour="k")
        return line_obj

    def add_markers(self, group_objects, line_objects):
        if self.markers:
            line_objects += [self.get_line_object_marker(group_obj)
                             for group_obj in group_objects]
        return line_objects

    def get_line_object_marker(self, group_obj):
        x_values = group_obj.spectrum_obj.peak_frequencies
        y_values = group_obj.spectrum_obj.peak_S21s
        line_obj = Line(x_values, y_values, colour="r", marker="*", linestyle="None")
        return line_obj

    def add_fit(self, group_objects, line_objects):
        if self.fit:
            for group_obj in group_objects:
                line_objects.append(self.get_line_obj_fit(group_obj))
        return line_objects

    def get_line_obj_fit(self, group_obj):
        x_values = group_obj.envelope_x_values
        y_values = group_obj.envelope_y_values
        line_obj = Line(x_values, y_values, colour="k")
        return line_obj

    def set_lines_labels(self, lines_obj, detuning_obj):
        lines_obj.title = f"Detuning: {detuning_obj.detuning} Hz"
        lines_obj.x_label = "Frequency (Hz)"
        lines_obj.y_label = "S21 (mW)"

    def create_plots(self, lines_objects, title):
        plot_obj = Plots(lines_objects, self.subplots, plot_type="semilogy")
        plot_obj.title = title
        plot_obj.plot()
