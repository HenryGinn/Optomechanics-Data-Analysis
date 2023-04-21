class Line():

    label_units = ""

    def __init__(self, x_values, y_values, label=None,
                 colour=None, marker=None, linestyle=None, linewidth=None):
        self.set_values(x_values, y_values)
        self.label = label
        self.set_line_properties(colour, marker, linestyle, linewidth)

    def set_values(self, x_values, y_values):
        self.x_values = x_values
        self.y_values = y_values

    def set_line_properties(self, colour, marker, linestyle, linewidth):
        self.colour = colour
        self.marker = marker
        self.linestyle = linestyle
        self.linewidth = linewidth
