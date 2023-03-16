import numpy as np

from Plot import Plot
from Utils import get_group_indexes

class Plots():

    def __init__(self, line_objects, group_size):
        self.line_objects = np.array(line_objects)
        self.total = len(line_objects)
        self.set_group_size(group_size)
        self.partition_line_objects()

    def set_group_size(self, group_size):
        if group_size is None:
            self.group_size = len(self.line_objects)
        else:
            self.group_size = group_size

    def partition_line_objects(self):
        group_indexes = get_group_indexes(self.total, self.group_size)
        self.line_object_groups = [self.line_objects[indexes] for indexes in group_indexes]
    
    def plot(self):
        for line_object_group in self.line_object_groups:
            plot = Plot(line_object_group)
            plot.create_figure()
