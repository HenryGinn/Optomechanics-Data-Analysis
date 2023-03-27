import numpy as np

from Plotting.Plot import Plot
from Plotting.PlotUtils import get_group_indexes
from Plotting.PlotUtils import get_group_size

class Plots():

    """
    An instance of Plots will represent several figures that are
    all associated with one list of objects. When wanting to plot
    multiple things, they might not all fit on one figure. Plots
    organises how they are put onto multiple figures, and each of
    those figures is handled as a single Plot object.
    """

    def __init__(self, lines_objects, subplot_count=None):
        self.process_lines_objects(lines_objects)
        self.process_subplots(subplot_count)

    def process_lines_objects(self, lines_objects):
        self.lines_objects = np.array(lines_objects)
        self.total = len(lines_objects)

    def process_subplots(self, subplot_count):
        self.set_subplot_count(subplot_count)
        self.partition_lines_objects()

    def set_subplot_count(self, subplot_count):
        self.subplot_count = get_group_size(subplot_count, self.lines_objects)

    def partition_lines_objects(self):
        group_indexes = get_group_indexes(self.total, self.subplot_count)
        self.lines_object_groups = [self.lines_objects[indexes]
                                    for indexes in group_indexes]
    
    def plot(self):
        for index, lines_object_group in enumerate(self.lines_object_groups):
            plot = Plot(self, lines_object_group, index)
            plot.create_figure()
