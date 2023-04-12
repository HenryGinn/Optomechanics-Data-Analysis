import os
import math

import matplotlib.pyplot as plt
import numpy as np

from Plotting.PlotShape import PlotShape
from Plotting.PlotUtils import update_figure_size
from Plotting.PlotUtils import get_prefixed_numbers
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

    title = "My Plot"
    save_format = "pdf"
    layouts = {"Constrained": True,
               "Tight": False,
               "Adjust": False}

    def __init__(self, plots_obj, lines_objects,
                 plot_index):
        self.plots_obj = plots_obj
        self.kwargs = plots_obj.kwargs
        self.process_lines_objects(lines_objects)
        self.plot_index = plot_index
        self.set_grid_size()

    def process_lines_objects(self, lines_objects):
        self.lines_objects = lines_objects
        self.count = len(self.lines_objects)
        if self.plots_obj.universal_legend:
            self.count += 1

    def set_grid_size(self):
        self.process_aspect_ratio()
        plot_shape_obj = PlotShape(self.count, self.aspect_ratio)
        self.rows, self.columns = plot_shape_obj.dimensions

    def process_aspect_ratio(self):
        self.aspect_ratio = self.plots_obj.aspect_ratio
        if "aspect_ratio" in self.kwargs:
            if self.kwargs["aspect_ratio"] is not None:
                self.aspect_ratio = self.kwargs["aspect_ratio"]
    
    def create_figure(self):
        self.process_layout_kwargs()
        self.fig, self.axes = plt.subplots(nrows=self.rows, ncols=self.columns,
                                           constrained_layout=self.layouts["Constrained"])
        self.plot_axes()
        self.add_plot_peripherals()
        self.modify_figure_sizes()
        plt.show()
        self.plot_positions = [plt.getp(ax, "position") for ax in self.axes]
        self.x_tick_labels = [plt.getp(ax, "xmajorticklabels") for ax in self.axes]
        self.x_lims = [plt.getp(ax, "xlim") for ax in self.axes]
        plt.close()
        self.fig, self.axes = plt.subplots(nrows=self.rows, ncols=self.columns)
        self.plot_axes()
        self.add_plot_peripherals()
        self.modify_figure_sizes()
        for ax, position in zip(self.axes, self.plot_positions):
            plt.setp(ax, position=position)
        for ax, x_tick_labels, x_lims in zip(self.axes, self.x_tick_labels, self.x_lims):
            text_data = [(text_obj._x, text_obj._y, text_obj._text)
                         for text_obj in x_tick_labels
                         if text_obj._x > x_lims[0] and text_obj._x < x_lims[1]]
            x, y, text = zip(*text_data)
            text = [self.convert_tick_label_to_floats(string) for string in text]
            tick_labels, prefix = get_prefixed_numbers(text)
            ax.set_xticks(x, labels=tick_labels)
        self.process_plot()
        plt.close()

    def convert_tick_label_to_floats(self, string):
        if ord(string[0]) == 8722:
            value = -float(string[1:])
        else:
            value = float(string)
        return value

    def process_layout_kwargs(self):
        if "layout" in self.kwargs:
            self.set_all_layouts_to_false()
            self.layouts[self.kwargs["layout"]] = True

    def set_all_layouts_to_false(self):
        for layout in self.layouts:
            self.layouts[layout] = False
    
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
        extra_axes = len(self.axes) - self.count
        for ax, _ in zip(self.axes[::-1], range(extra_axes)):
            ax.remove()

    def add_plot_peripherals(self):
        self.set_suptitle()
        self.set_legend()

    def set_suptitle(self):
        if hasattr(self.plots_obj, "title"):
            self.fig.suptitle(f"{self.plots_obj.title}")

    def set_legend(self):
        if self.plots_obj.universal_legend:
            self.do_universal_legend()
        else:
            self.do_non_universal_legends()

    def do_universal_legend(self):
        ax = self.axes[-1]
        for line_obj in self.lines_objects[0].line_objects:
            ax.plot(1, 1, label=line_obj.label, color=line_obj.colour)
        ax.legend(loc="center", borderpad=2, labelspacing=1)
        ax.axis("off")

    def do_non_universal_legends(self):
        for ax, lines_obj in zip(self.axes, self.lines_objects):
            if lines_obj.legend:
                ax.legend(loc=lines_obj.legend_loc)

    def modify_figure_sizes(self):
        self.set_figure_size()
        self.adjust_layout()

    def set_figure_size(self):
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        #mng.window.fullscreen()

    def adjust_layout(self):
        if self.layouts["Adjust"]:
            plt.subplot_tool()
        elif self.layouts["Tight"]:
            plt.tight_layout()

    def process_plot(self):
        if not ("show" in self.kwargs and not self.kwargs["show"]):
            plt.show()
        if not("save" in self.kwargs and not self.kwargs["save"]):
            self.save_plot()

    def save_plot(self):
        file_name_data = self.get_file_name_data()
        self.path = f"{self.plots_obj.base_path}{file_name_data}"
        self.set_save_format()
        self.fig.savefig(self.path, format=self.save_format, dpi=self.fig.dpi, bbox_inches='tight')

    def get_file_name_data(self):
        file_name_data = ""
        if len(self.plots_obj.lines_object_groups) > 1:
            file_name_data = f"_{self.plot_index + 1}"
        return file_name_data

    def set_save_format(self):
        if "format" in self.kwargs:
            self.save_format = self.kwargs["format"]
