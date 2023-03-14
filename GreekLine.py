import numpy as np

class GreekLine():

    def __init__(self, greek_child):
        self.detuning = greek_child.detuning
        self.label = greek_child.label
        self.x_values = greek_child.x_values
