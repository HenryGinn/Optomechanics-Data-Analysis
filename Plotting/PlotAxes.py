import matplotlib.pyplot as plt

from Plotting.PlotUtils import get_prefixed_numbers

class PlotAxes():

    def __init__(self, plot_obj):
        self.plot_obj = plot_obj
        self.fig = plot_obj.fig
        self.axes = plot_obj.axes

    def improve_axes(self):
        self.set_subplot_positions()
        self.set_improved_x_axis_labels()
        self.set_improved_y_axis_labels()

    def set_subplot_positions(self):
        for ax, position in zip(self.axes, self.plot_obj.plot_positions):
            plt.setp(ax, position=position)

    def set_improved_x_axis_labels(self):
        figure_data_iterable = self.get_figure_data_iterable_x()
        for ax, x_tick_labels, x_lims in figure_data_iterable:
            self.set_improved_x_axis_labels_subplot(ax, x_tick_labels, x_lims)

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

    def get_labels_data_x(self, tick_labels, limits):
        labels_data = [(text_obj._x, text_obj._y, text_obj._text)
                       for text_obj in tick_labels
                       if text_obj._x > limits[0] and text_obj._x < limits[1]]
        return labels_data

    def set_improved_y_axis_labels(self):
        figure_data_iterable = self.get_figure_data_iterable_y()
        for ax, y_tick_labels, y_lims in figure_data_iterable:
            self.set_improved_y_axis_labels_subplot(ax, y_tick_labels, y_lims)

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

    def set_x_label(self, ax, lines_obj):
        if hasattr(lines_obj, "x_label"):
            ax.set_xlabel(lines_obj.x_label)

    def set_y_label(self, ax, lines_obj):
        if hasattr(lines_obj, "y_label"):
            ax.set_ylabel(lines_obj.y_label)

