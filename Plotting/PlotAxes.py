import matplotlib.pyplot as plt
import numpy as np

from Plotting.PlotUtils import get_prefixed_numbers
from Plotting.PlotUtils import reverse_prefix_lookup

class PlotAxes():

    def __init__(self, plot_obj):
        self.plot_obj = plot_obj
        self.fig = plot_obj.fig
        self.axes = plot_obj.axes

    def improve_axes(self):
        self.set_subplot_positions()
        self.set_improved_x_axis()
        self.set_improved_y_axis()

    def set_subplot_positions(self):
        for ax, position in zip(self.axes, self.plot_obj.plot_positions):
            plt.setp(ax, position=position)

    def set_improved_x_axis(self):
        figure_data_iterable = self.get_figure_data_iterable_x()
        prefixes_x = [self.set_improved_x_axis_labels_subplot(ax, x_tick_labels, x_lims)
                      for ax, x_tick_labels, x_lims in figure_data_iterable]
        self.set_improved_x_axis_labels(prefixes_x)

    def get_figure_data_iterable_x(self):
        figure_data_iterable = zip(self.plot_obj.axes,
                                   self.plot_obj.x_tick_labels_figure,
                                   self.plot_obj.figure_x_lims)
        return figure_data_iterable

    def set_improved_x_axis_labels_subplot(self, ax, x_tick_labels, x_lims):
        labels_data = self.get_labels_data_x(x_tick_labels, x_lims)
        tick_positions, _, tick_labels = zip(*labels_data)
        tick_labels, prefix = self.process_tick_labels(tick_labels)
        ax.set_xticks(tick_positions, labels=tick_labels)
        return prefix

    def get_labels_data_x(self, tick_labels, limits):
        labels_data = [(text_obj._x, text_obj._y, text_obj._text)
                       for text_obj in tick_labels
                       if text_obj._x > limits[0] and text_obj._x < limits[1]]
        return labels_data

    def set_improved_y_axis(self):
        figure_data_iterable = self.get_figure_data_iterable_y()
        prefixes_y = [self.set_improved_y_axis_labels_subplot(ax, y_tick_labels, y_lims)
                      for ax, y_tick_labels, y_lims in figure_data_iterable]
        self.set_improved_y_axis_labels(prefixes_y)

    def get_figure_data_iterable_y(self):
        figure_data_iterable = zip(self.plot_obj.axes,
                                   self.plot_obj.y_tick_labels_figure,
                                   self.plot_obj.figure_y_lims)
        return figure_data_iterable

    def set_improved_y_axis_labels_subplot(self, ax, y_tick_labels, y_lims):
        labels_data = self.get_labels_data_y(y_tick_labels, y_lims)
        _, tick_positions, tick_labels = zip(*labels_data)
        tick_labels, prefix = self.process_tick_labels(tick_labels)
        ax.set_yticks(tick_positions, labels=tick_labels)
        return prefix

    def get_labels_data_y(self, tick_labels, limits):
        labels_data = [(text_obj._x, text_obj._y, text_obj._text)
                       for text_obj in tick_labels
                       if text_obj._y > limits[0] and text_obj._y < limits[1]]
        return labels_data

    def process_tick_labels(self, tick_labels):
        tick_labels = [self.convert_tick_label_to_floats(string) for string in tick_labels]
        tick_labels, prefix = get_prefixed_numbers(tick_labels)
        return tick_labels, prefix

    def convert_tick_label_to_floats(self, string):
        if ord(string[0]) == 8722:
            value = -float(string[1:])
        else:
            value = float(string)
        return value


    def set_axes_labels(self, ax, lines_obj):
        self.set_x_label(ax, lines_obj)
        self.set_y_label(ax, lines_obj)

    def set_x_label(self, ax, lines_obj, prefix=None):
        prefix = self.set_default_prefix(prefix)
        if hasattr(lines_obj, "x_label"):
            if lines_obj.x_label is not None:
                self.do_set_x_label(ax, lines_obj, prefix)

    def do_set_x_label(self, ax, lines_obj, prefix):
        label = lines_obj.x_label
        label = self.add_x_label_prefix(lines_obj, label, prefix)
        ax.set_xlabel(label)

    def add_x_label_prefix(self, lines_obj, label, prefix):
        if lines_obj.x_label_type == "Prefix":
            label = self.add_prefix(label, lines_obj.x_units, prefix)
        elif lines_obj.x_label_type == "Count":
            label = self.add_count(label, prefix)
        return label

    def set_y_label(self, ax, lines_obj, prefix=None):
        prefix = self.set_default_prefix(prefix)
        if hasattr(lines_obj, "y_label"):
            if lines_obj.y_label is not None:
                self.do_set_y_label(ax, lines_obj, prefix)

    def do_set_y_label(self, ax, lines_obj, prefix):
        label = lines_obj.y_label
        label = self.add_y_label_prefix(lines_obj, label, prefix)
        ax.set_ylabel(label)

    def add_y_label_prefix(self, lines_obj, label, prefix):
        if lines_obj.y_label_type == "Prefix":
            label = self.add_prefix(label, lines_obj.y_units, prefix)
        elif lines_obj.y_label_type == "Count":
            label = self.add_count(label, prefix)
        return label

    def add_prefix(self, label, units, prefix):
        if units is not None:
            label = f"{label} ({prefix}{units})"
        elif prefix is not None:
            label = self.incorrect_units_type(label, prefix)
        return label

    def incorrect_units_type(self, label, prefix):
        label = add_count(label, prefix)
        print("Warning: a Lines object was given units type 'Prefix' but no units\n"
              "It is being assumed to be unitless (do not ignore, there's probably an error)")
        return label

    def add_count(self, label, prefix):
        if prefix != "":
            magnitude = self.get_magnitude(prefix)
            label = f"{label} ({magnitude})"
        return label

    def get_magnitude(self, prefix):
        zeros = 3 * reverse_prefix_lookup(prefix)
        if zeros > 0:
            magnitude = f"1{zeros * '0'}s"
        else:
            magnitude = f"0.{(- 1 - zeros)*'0'}1s"
        return magnitude

    def set_default_prefix(self, prefix):
        if prefix is None:
            prefix = ""
        return prefix

    def set_improved_x_axis_labels(self, prefixes_x):
        for lines_obj, ax, prefix in zip(self.plot_obj.lines_objects, self.axes, prefixes_x):
            self.set_x_label(ax, lines_obj, prefix=prefix)

    def set_improved_y_axis_labels(self, prefixes_y):
        for lines_obj, ax, prefix in zip(self.plot_obj.lines_objects, self.axes, prefixes_y):
            self.set_y_label(ax, lines_obj, prefix=prefix)
