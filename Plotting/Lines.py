import numpy as np
from matplotlib.colors import hsv_to_rgb

class Lines():

    def __init__(self, line_objects):
        self.line_objects = line_objects
        self.count = len(line_objects)
        self.set_legend(False)

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
