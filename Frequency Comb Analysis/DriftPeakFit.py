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

    def plot_peak_fits(self, groups):
        group_indexes = self.get_group_indexes(groups)
        self.set_x_values()
        lines_objects = [self.get_lines_obj(indexes) for indexes in group_indexes]
        plots_obj = Plots(lines_objects, subplot_count=None)
        plots_obj.plot()

    def get_group_indexes(self, groups):
        group_count = len(set(self.group_numbers))
        detuning_range = np.arange(0, len(self.group_numbers), group_count)
        group_indexes = [group_index + detuning_range
                         for group_index in range(group_count)]
        print(group_indexes)
        print(groups)
        group_indexes = get_sliced_list(group_indexes, groups)
        print(group_indexes)
        return group_indexes

    def set_x_values(self):
        self.left_x_values = np.array([-10**6, 0])
        self.right_x_values = np.array([0, 10**6])

    def get_lines_obj(self, indexes):
        line_objects = [self.get_line_obj_pair(index) for index in indexes]
        line_objects = flatten_by_one(line_objects)
        lines_obj = Lines(line_objects)
        lines_obj = self.get_lines_labels(lines_obj)
        return lines_obj

    def get_line_obj_pair(self, index):
        left_line = self.get_left_line(index)
        right_line = self.get_right_line(index)
        return (left_line, right_line)

    def get_left_line(self, index):
        gradient = self.left_gradients[index]
        intercept = self.left_intercepts[index]
        y_values = evaluate_line(self.left_x_values, (gradient, intercept))
        line_obj = Line(self.left_x_values, y_values)
        return line_obj

    def get_right_line(self, index):
        gradient = self.right_gradients[index]
        intercept = self.right_intercepts[index]
        y_values = evaluate_line(self.right_x_values, (gradient, intercept))
        line_obj = Line(self.right_x_values, y_values)
        return line_obj

    def get_lines_labels(self, lines_obj):
        lines_obj.title = "My Title"
        lines_obj.x_label = "My x label"
        lines_obj.y_label = "My y label"
        return lines_obj
