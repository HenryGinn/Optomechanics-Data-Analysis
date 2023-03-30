import math

import matplotlib.pyplot as plt
import numpy as np

from Plotting.PlotShape import PlotShape
from Plotting.PlotUtils import update_figure_size
from Plotting.PlotUtils import get_pretty_axis
from Plotting.PlotUtils import adjust_subplots

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class Plot():

    """
    An instance of Plot will be a single figure.
    This figure can have multiple subplots, and corresponding to
    each subplot is a Lines object. A Lines object has a collection
    of Line objects associated with it.
    """

    def __init__(self, plots_obj, lines_objects,
                 plot_index, aspect_ratio=None):
        self.plots_obj = plots_obj
        self.process_lines_objects(lines_objects)
        self.plot_index = plot_index
        self.set_grid_size(aspect_ratio)

    def process_lines_objects(self, lines_objects):
        self.lines_objects = lines_objects
        self.count = len(self.lines_objects)

    def set_grid_size(self, aspect_ratio):
        self.process_aspect_ratio(aspect_ratio)
        plot_shape_obj = PlotShape(self.count, self.aspect_ratio)
        self.rows, self.columns = plot_shape_obj.dimensions

    def process_aspect_ratio(self, aspect_ratio):
        if aspect_ratio is not None:
            self.aspect_ratio = aspect_ratio
        else:
            self.aspect_ratio = self.plots_obj.aspect_ratio
    
    def create_figure(self, **kwargs):
        fig, self.axes = plt.subplots(nrows=self.rows, ncols=self.columns)
        self.plot_axes()
        self.add_plot_peripherals(fig)
        self.modify_figure_sizes(**kwargs)
        self.show_plot(fig)

    def plot_axes(self):
        self.flatten_axes()
        for ax, lines_obj in zip(self.axes, self.lines_objects):
            self.plot_lines(ax, lines_obj)
            self.set_labels(ax, lines_obj)
        self.remove_extra_axes()

    def plot_lines(self, ax, lines_obj):
        plot_function = self.get_plot_function(ax, lines_obj)
        for line_obj in lines_obj.line_objects:
            self.plot_line(ax, line_obj, plot_function)
        lines_obj.set_limits()
        #self.prettify_axes(ax, lines_obj)

    def get_plot_function(self, ax, lines_obj):
        plot_functions = {"plot": ax.plot,
                          "semilogy": ax.semilogy}
        plot_function = plot_functions[lines_obj.plot_type]
        return plot_function
        
    def plot_line(self, ax, line_obj, plot_function):
        plot_function(line_obj.x_values, line_obj.y_values,
                      color=line_obj.colour,
                      marker=line_obj.marker,
                      linestyle=line_obj.linestyle,
                      label=line_obj.label)

    def set_labels(self, ax, lines_obj):
        self.set_title(ax, lines_obj)
        self.set_x_label(ax, lines_obj)
        self.set_y_label(ax, lines_obj)

    def set_title(self, ax, lines_obj):
        if hasattr(lines_obj, "title"):
            ax.set_title(lines_obj.title)

    def set_x_label(self, ax, lines_obj):
        if hasattr(lines_obj, "x_label"):
            ax.set_xlabel(lines_obj.x_label)

    def set_y_label(self, ax, lines_obj):
        if hasattr(lines_obj, "y_label"):
            ax.set_ylabel(lines_obj.y_label)

    def flatten_axes(self):
        if isinstance(self.axes, np.ndarray):
            self.axes = self.axes.flatten()
        else:
            self.axes = [self.axes]

    def remove_extra_axes(self):
        extra_axes = len(self.axes) - len(self.lines_objects)
        for ax, _ in zip(self.axes[::-1], range(extra_axes)):
            ax.remove()

    def add_plot_peripherals(self, fig):
        self.set_suptitle(fig)
        self.set_legend(fig)

    def set_suptitle(self, fig):
        if hasattr(self.plots_obj, "title"):
            fig.suptitle(f"{self.plots_obj.title}")

    def set_legend(self, fig):
        for ax, lines_obj in zip(self.axes, self.lines_objects):
            if lines_obj.legend:
                ax.legend(loc=lines_obj.legend_loc)

    def prettify_axes(self, ax, lines_obj):
        self.prettify_x_axis(ax, lines_obj.x_limits)
        self.prettify_y_axis(ax, lines_obj.y_limits)

    def modify_figure_sizes(self, **kwargs):
        adjust_subplots()
        self.add_subplot_tool(**kwargs)

    def add_subplot_tool(self, **kwargs):
        if "adjust" in kwargs:
            if kwargs["adjust"]:
                plt.subplot_tool()

    def prettify_x_axis(self, ax, limits):
        tick_positions, tick_labels, offset, prefix = get_pretty_axis(limits)
        ax.set_xticks(tick_positions, labels=tick_labels)
        print(prefix)

    def prettify_y_axis(self, ax, limits):
        tick_positions, tick_labels, offset, prefix = get_pretty_axis(limits)
        ax.set_yticks(tick_positions, labels=tick_labels)
        print(prefix)

    def show_plot(self, fig):
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()
        plt.close()
