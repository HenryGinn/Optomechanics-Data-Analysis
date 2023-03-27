import numpy as np
from matplotlib.colors import hsv_to_rgb

class Lines():

    def __init__(self, line_objects, plot_type="plot", legend=None):
        self.line_objects = line_objects
        self.count = len(line_objects)
        self.process_plot_options(plot_type, legend)

    def process_plot_options(self, plot_type, legend):
        self.plot_type = plot_type
        self.legend = legend

    def set_rainbow_lines(self):
        self.set_colours()
        for line_obj, colour in zip(self.line_objects, self.colours):
            line_obj.colour = colour

    def set_colours(self):
        hues = np.linspace(0, 1, self.count + 1)[:self.count]
        saturations = np.ones(self.count)
        values = np.ones(self.count)
        hsv_tuples = np.array(list(zip(hues, saturations, values)))
        self.colours = hsv_to_rgb(hsv_tuples)

    def set_legend(self, legend, loc=0):
        self.legend = legend
        self.legend_loc = loc

    def set_limits(self):
        self.set_x_limits()
        self.set_y_limits()

    def set_x_limits(self):
        x_limit_lower = min([min(line_obj.x_values) for line_obj in self.line_objects])
        x_limit_upper = max([max(line_obj.x_values) for line_obj in self.line_objects])
        self.x_limits = [x_limit_lower, x_limit_upper]

    def set_y_limits(self):
        y_limit_lower = min([min(line_obj.y_values) for line_obj in self.line_objects])
        y_limit_upper = max([max(line_obj.y_values) for line_obj in self.line_objects])
        self.y_limits = [y_limit_lower, y_limit_upper]
