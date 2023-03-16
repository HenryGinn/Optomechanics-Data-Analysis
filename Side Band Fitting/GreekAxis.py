import os
import sys
import math

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class GreekAxis():

    """
    This is responsible for an axis of a figure. It is managed by
    GreekFigure and should produce GreekLine objects, and use them
    to plot onto the axis.
    """

    def __init__(self, trial_obj, axis):
        self.trial_obj = trial_obj
        self.axis = axis

    def plot_lines(self):
        for greek_line in self.lines:
            self.make_plot_of_greek(greek_line)

    def make_plot_of_greek(self, greek_line):
        if hasattr(greek_line, 'deviations') is False:
            self.axis.plot(greek_line.x_values, greek_line.greek, '.-', label=greek_line.label)
        else:
            self.axis.errorbar(greek_line.x_values, greek_line.greek, fmt='.-', yerr=greek_line.deviations, label=greek_line.label)

    def add_x_axis_labels(self):
        self.remove_edge_x_ticks()
        prefix, prefix_power = self.get_prefix_data()
        x_ticks = self.axis.get_xticks()
        x_labels = [f'{value:.0f}' for value in x_ticks/1000**prefix_power]
        self.axis.set_xticks(x_ticks, x_labels)
        self.axis.set_xlabel(r"Detuning $\left(\Delta = \frac{\omega_d - \omega_0}{2\pi}\right)$ "+ f"({prefix})")

    def remove_edge_x_ticks(self):
        x_ticks, x_labels = self.axis.get_xticks(), self.axis.get_xticklabels()
        x_ticks = x_ticks[1:-1]
        x_labels = x_labels[1:-1]
        self.axis.set_xticks(x_ticks, x_labels)

    def get_prefix_data(self):
        x_ticks = self.axis.get_xticks()
        max_x_tick = max(abs(x_ticks))
        prefix_power = math.floor(math.log(max_x_tick, 1000))
        prefix = {-1: "mHz", 0: "Hz", 1: "kHz", 2: "MHz", 3: "GHz", 4: "THz"}[prefix_power]
        return prefix, prefix_power

    def add_y_axis_labels(self):
        self.reset_y_ticks_and_labels()
        self.axis.set_ylabel(f"{self.name_latex} ({self.units})")

    def reset_y_ticks_and_labels(self):
        # This code appears unnecessary but ticks can go missing if it is not included
        y_ticks = self.axis.get_yticks()
        y_labels = self.axis.get_yticklabels()
        self.axis.set_yticks(y_ticks, y_labels)
