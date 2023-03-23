import numpy as np

from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from PeakLine import evaluate_line
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
         self.left_gradients, self.left_intercepts,
         self.right_gradients, self.right_intercepts) = file_contents

    def plot_peak_fits(self, groups, legend):
        lines_objects = self.get_lines_objects(groups)
        plots_obj = Plots(lines_objects, plot_type="semilogy", legend=legend)
        plots_obj.title = f"Envelope of Frequency Comb Peaks for {self.drift_obj}"
        plots_obj.plot()

    def get_lines_objects(self, groups):
        group_indexes = self.get_group_indexes(groups)
        self.set_x_values()
        lines_objects = [self.get_lines_obj(group_number, indexes)
                         for group_number, indexes in enumerate(group_indexes)]
        return lines_objects

    def get_group_indexes(self, groups):
        group_count = len(set(self.group_numbers))
        detuning_range = np.arange(0, len(self.group_numbers), group_count)
        group_indexes = [group_index + detuning_range
                         for group_index in range(group_count)]
        group_indexes = get_sliced_list(group_indexes, groups)
        return group_indexes

    def set_x_values(self):
        self.left_x_values = np.array([-10**6, 0])
        self.right_x_values = np.array([0, 10**6])

    def get_lines_obj(self, group_number, indexes):
        line_objects = [self.get_line_obj(index) for index in indexes]
        lines_obj = Lines(line_objects)
        lines_obj = self.get_lines_labels(lines_obj, group_number)
        lines_obj.set_rainbow_lines()
        return lines_obj

    def get_line_obj(self, index):
        label = self.detunings[index]
        y_values = self.get_y_values(index)
        x_values = np.concatenate((self.left_x_values, self.right_x_values))
        line_obj = Line(x_values, y_values, label=label)
        return line_obj

    def get_y_values(self, index):
        left_y_values = self.get_left_y_values(index)
        right_y_values = self.get_right_y_values(index)
        y_values = np.concatenate((left_y_values, right_y_values))
        y_values = np.exp(y_values)
        return y_values

    def get_left_y_values(self, index):
        gradient = self.left_gradients[index]
        intercept = self.left_intercepts[index]
        left_y_values = evaluate_line(self.left_x_values, (gradient, intercept))
        return left_y_values

    def get_right_y_values(self, index):
        gradient = self.right_gradients[index]
        intercept = self.right_intercepts[index]
        right_y_values = evaluate_line(self.right_x_values, (gradient, intercept))
        return right_y_values

    def get_lines_labels(self, lines_obj, group_number):
        lines_obj.title = f"Group {group_number}"
        lines_obj.x_label = "Frequency (Hz)"
        lines_obj.y_label = "S21 (mW)"
        return lines_obj
