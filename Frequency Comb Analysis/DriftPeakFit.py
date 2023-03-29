import numpy as np

from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Plotting.PlotUtils import get_prefixed_number
from Utils import get_file_contents_from_path
from Utils import flatten_by_one
from Utils import get_sliced_list

class DriftPeakFit():

    def __init__(self, drift_obj):
        self.drift_obj = drift_obj

    def load_peak_fits(self):
        path = self.drift_obj.peak_fit_path
        file_contents = get_file_contents_from_path(path)
        self.load_from_file_contents(file_contents)

    def load_from_file_contents(self, file_contents):
        (self.detunings, self.group_numbers,
         self.gradients, self.intercepts) = file_contents
        self.update_drift_objects()

    def update_drift_objects(self):
        group_number = 0
        for detuning_obj in self.drift_obj.detuning_objects:
            for group_obj in detuning_obj.group_objects:
                self.update_group_obj(group_obj, group_number)
                group_number += 1

    def update_group_obj(self, group_obj, group_number):
        group_obj.peaks_fit_obj = FitPeaks(group_obj)
        gradient = self.gradients[group_number]
        intercept = self.intercepts[group_number]
        group_obj.peaks_fit_obj.fitting_parameters = [gradient, intercept]
        group_obj.set_envolope_values()

    def plot_peak_fits(self, groups, legend):
        lines_objects = self.get_lines_objects(groups)
        plots_obj = Plots(lines_objects, plot_type="semilogy", legend=legend)
        plots_obj.title = f"Envelopes of Frequency Comb Peaks for {self.drift_obj}"
        plots_obj.plot()

    def get_lines_objects(self, groups):
        group_indexes = self.get_group_indexes(groups)
        lines_objects = [self.get_lines_obj(indexes)
                         for indexes in group_indexes]
        return lines_objects

    def get_group_indexes(self, groups):
        group_count = len(set(self.group_numbers))
        detuning_range = np.arange(0, len(self.group_numbers), group_count)
        group_indexes = [group_index + detuning_range
                         for group_index in range(group_count)]
        group_indexes = get_sliced_list(group_indexes, groups)
        return group_indexes

    def get_lines_obj(self, indexes):
        line_objects = [self.get_line_obj(index) for index in indexes]
        lines_obj = Lines(line_objects)
        lines_obj = self.get_lines_labels(lines_obj, indexes[0])
        lines_obj.set_rainbow_lines()
        return lines_obj

    def get_line_obj(self, index):
        label = get_prefixed_number(self.detunings[index])
        gradient = self.gradients[index]
        intercept = self.intercepts[index]
        line_obj = self.get_line_from_parameters(gradient, intercept, label)
        return line_obj

    def get_line_from_parameters(self, gradient, intercept, label):
        x_values = np.array([-2.5e5, 0, 2.5e5])
        y_values = evaluate_abs(x_values, (gradient, intercept))
        y_values = np.exp(y_values)
        line_obj = Line(x_values, y_values, label=label)
        return line_obj

    def get_lines_labels(self, lines_obj, index):
        lines_obj.title = f"Group {self.group_numbers[index]}"
        lines_obj.x_label = "Frequency (Hz)"
        lines_obj.y_label = "S21 (mW)"
        return lines_obj
