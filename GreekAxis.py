import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import math

plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['axes.formatter.limits'] = [-5,5]

class GreekAxis():

    """
    This is responsible for an axis of a figure. It is managed by
    GreekFigure and should produce GreekLine objects, and use them
    to plot onto the axis.
    """

    def __init__(self, trial_obj, greek_obj, axis):
        self.trial_obj = trial_obj
        self.axis = axis
        self.greek_obj = greek_obj
        self.greek_children = []

    def plot_greek_child(self, greek_child):
        self.greek_children.append(greek_child)
        self.make_plot_of_greek(greek_child)

    def make_plot_of_greek(self, greek_child):
        if hasattr(greek_child, 'deviations') is False:
            self.axis.plot(greek_child.x_values, greek_child.greek, '.-', label=greek_child.label)
        else:
            self.axis.errorbar(greek_child.x_values, greek_child.greek, fmt='.-', yerr=greek_child.deviations, label=greek_child.label)

    def add_plot_labels(self):
        self.add_axis_labels()
        self.axis.legend(bbox_to_anchor=(1.05, 1), loc = 2)

    def add_axis_labels(self):
        self.add_x_axis_labels()
        self.add_y_axis_labels()

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
        self.axis.set_ylabel(f"{self.greek_obj.name_latex} (Hz)")

    def reset_y_ticks_and_labels(self):
        # This code appears unnecessary but ticks can go missing if it is not included
        y_ticks = self.axis.get_yticks()
        y_labels = self.axis.get_yticklabels()
        self.axis.set_yticks(y_ticks, y_labels)
