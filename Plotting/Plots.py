import os

import numpy as np

from Plotting.Plot import Plot
from Plotting.PlotUtils import get_group_indexes
from Plotting.PlotUtils import get_group_size
from Utils import make_folder

class Plots():

    """
    An instance of Plots will represent several figures that are
    all associated with one list of objects. When wanting to plot
    multiple things, they might not all fit on one figure. Plots
    organises how they are put onto multiple figures, and each of
    those figures is handled as a single Plot object.
    """

    aspect_ratio = 2
    title = "My Plot"

    def __init__(self, lines_objects, kwargs, universal_legend=False):
        self.process_lines_objects(lines_objects)
        self.universal_legend = universal_legend
        self.kwargs = kwargs
        self.process_kwargs()

    def process_lines_objects(self, lines_objects):
        self.lines_objects = np.array(lines_objects)
        self.total = len(lines_objects)

    def process_kwargs(self):
        self.process_subplots()
        self.process_aspect_ratio()

    def process_subplots(self):
        self.set_subplot_count()
        self.partition_lines_objects()

    def set_subplot_count(self):
        subplot_count = None
        if "subplots" in self.kwargs:
            subplot_count = self.kwargs["subplots"]
        self.subplot_count = get_group_size(subplot_count, self.lines_objects)

    def partition_lines_objects(self):
        group_indexes = get_group_indexes(self.total, self.subplot_count)
        self.lines_object_groups = [self.lines_objects[indexes]
                                    for indexes in group_indexes]

    def process_aspect_ratio(self):
        if "aspect_ratio" in self.kwargs:
            self.aspect_ratio = self.kwargs["aspect_ratio"]
    
    def plot(self):
        self.set_paths()
        for index, lines_object_group in enumerate(self.lines_object_groups):
            plot_obj = Plot(self, lines_object_group, index)
            plot_obj.title = self.title
            plot_obj.create_figure()

    def set_paths(self):
        plot_folder_name = self.get_plot_folder_name()
        self.results_path = os.path.join(self.parent_results_path, "Plots")
        make_folder(self.results_path)
        self.base_path = os.path.join(self.results_path, self.title)

    def get_plot_folder_name(self):
        if len(self.lines_object_groups) == 1:
            plot_folder_name = f"{self.title} Plots"
        else:
            plot_folder_name = f"{self.title}_Subplots_{self.subplot_count} Plots"
        return plot_folder_name
