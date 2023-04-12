import numpy as np
from matplotlib.colors import hsv_to_rgb

class Lines():

    x_units = ""
    x_units_type = "Count"
    y_units = ""
    y_units_type = "Count"

    def __init__(self, line_objects, plot_type="plot",
                 legend=None, legend_loc=0):
        self.line_objects = line_objects
        self.count = len(line_objects)
        self.process_plot_options(plot_type, legend, legend_loc)

    def process_plot_options(self, plot_type, legend, legend_loc):
        self.plot_type = plot_type
        self.set_legend(legend, legend_loc)

    def set_rainbow_lines(self, saturation=1, value=1):
        self.set_colours(saturation, value)
        for line_obj, colour in zip(self.line_objects, self.colours):
            line_obj.colour = colour

    def set_colours(self, saturation, value):
        hues = np.linspace(0, 1, self.count + 1)[:self.count]
        saturations = np.ones(self.count)*saturation
        values = np.ones(self.count)*value
        hsv_tuples = np.array(list(zip(hues, saturations, values)))
        self.colours = hsv_to_rgb(hsv_tuples)

    def set_legend(self, legend, loc=0):
        self.legend = legend
        self.legend_loc = loc
