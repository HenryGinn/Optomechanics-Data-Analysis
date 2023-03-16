import os

import matplotlib.pyplot as plt
import numpy as np

from GreekAxis import GreekAxis
from GreekTrial import GreekTrial
from GreekLine import GreekLine

class GreekFigure():

    """
    This handles a figure involving Omega or Gamma data at the trial level.
    It manages OmegaTrial and GammaTrial objects, and is an interface
    for GreekAxis.
    """

    def __init__(self, trial_obj):
        self.trial = trial_obj

    def create_greek_figure(self, format_type):
        self.set_greek_obj()
        if self.greek_files_valid():
            self.do_create_greek_figure(format_type)
        
    def set_greek_obj(self):
        self.greek_obj = GreekTrial(self.trial)
        self.greek_obj.path = self.trial.data_set.greek_path
        self.greek_obj.set_files()
        self.greek_obj.set_children()

    def greek_files_valid(self):
        greek_non_empty = self.file_list_has_data(self.greek_obj.path, self.greek_obj.files)
        return greek_non_empty

    def do_create_greek_figure(self, format_type):
        #self.fig, (axis_omega, axis_gamma, axis_amplitude) = plt.subplots(3, sharex=True)
        self.fig, (axis_omega, axis_gamma) = plt.subplots(2, sharex=True)
        self.plot_greeks(axis_omega, axis_gamma, None)
        self.add_greek_figure_labels()
        self.save_greek_figure(format_type)

    def plot_greeks(self, axis_omega, axis_gamma, axis_amplitude):
        self.create_greek_axes(axis_omega, axis_gamma, axis_amplitude)
        self.fit_greek_axes()
        self.plot_greek_axes()

    def create_greek_axes(self, axis_omega, axis_gamma, axis_amplitude):
        self.create_omega_axis(axis_omega)
        self.create_gamma_axis(axis_gamma)
        #self.create_amplitude_axis(axis_amplitude)
        self.greek_axes = [self.omega_axis, self.gamma_axis]#, self.amplitude_axis]

    def create_omega_axis(self, axis):
        self.omega_axis = GreekAxis(self.trial, axis)
        self.set_omega_axis_names()
        self.omega_axis.lines = [self.get_omega_line(child)
                                 for child in self.greek_obj.children]

    def set_omega_axis_names(self):
        self.omega_axis.name = "Omega"
        self.omega_axis.name_latex = "$\Omega_m$"
        self.omega_axis.units = "Hz"

    def get_omega_line(self, child):
        line = GreekLine(child)
        child.omega = np.abs(child.omega)
        child.set_omega_offset()
        line.greek = child.omega_offset
        if hasattr(child, "omega_deviations"):
            line.deviations = child.omega_deviations
        return line

    def create_gamma_axis(self, axis):
        self.gamma_axis = GreekAxis(self.trial, axis)
        self.set_gamma_axis_names()
        self.gamma_axis.lines = [self.get_gamma_line(child)
                                 for child in self.greek_obj.children]

    def set_gamma_axis_names(self):
        self.gamma_axis.name = "Gamma"
        self.gamma_axis.name_latex = "$\Gamma_m$"
        self.gamma_axis.units = "Hz"

    def get_gamma_line(self, child):
        line = GreekLine(child)
        line.greek = child.gamma
        if hasattr(child, "gamma_deviations"):
            line.deviations = child.gamma_deviations
        return line

    def create_amplitude_axis(self, axis):
        self.amplitude_axis = GreekAxis(self.trial, axis)
        self.set_amplitude_axis_names()
        self.amplitude_axis.lines = [self.get_amplitude_line(child)
                                     for child in self.greek_obj.children]

    def set_amplitude_axis_names(self):
        self.amplitude_axis.name = "Amplitude"
        self.amplitude_axis.name_latex = "Amplitude"
        self.amplitude_axis.units = "dBm"

    def get_amplitude_line(self, child):
        line = GreekLine(child)
        line.greek = child.amplitude
        if hasattr(child, "amplitude_deviations"):
            line.deviations = child.amplitude_deviations
        return line

    def fit_greek_axes(self):
        for greek_child in self.greek_obj.children:
            #self.fit_omega(greek_child)
            self.fit_gamma(greek_child)
            pass

    def fit_omega(self, greek_child):
        omega_fitting_parameters = greek_child.get_omega_fitting_parameters()
        line = GreekLine(greek_child)
        line.label = f"{line.label} Fit"
        line.greek = greek_child.evaluate_omega_curve(omega_fitting_parameters)
        self.omega_axis.lines.append(line)

    def fit_gamma(self, greek_child):
        gamma_fitting_parameters = greek_child.get_gamma_fitting_parameters()
        print(gamma_fitting_parameters)
        line = GreekLine(greek_child)
        line.label = f"{line.label} Fit"
        line.greek = greek_child.evaluate_gamma_curve(gamma_fitting_parameters)
        self.gamma_axis.lines.append(line)

    def plot_greek_axes(self):
        for greek_axis in self.greek_axes:
            greek_axis.plot_lines()
            greek_axis.axis.legend(bbox_to_anchor=(1.05, 1), loc = 2)

    def add_greek_figure_labels(self):
        self.add_figure_title()
        self.add_y_axis_labels()
        self.gamma_axis.add_x_axis_labels()
        #self.amplitude_axis.add_x_axis_labels()

    def add_y_axis_labels(self):
        self.omega_axis.add_y_axis_labels()
        self.gamma_axis.add_y_axis_labels()
        #self.amplitude_axis.add_y_axis_labels()
    
    def save_greek_figure(self, format_type):
        figure_file_name = self.get_figure_file_name(format_type, "OmegaAndGamma")
        figure_path = os.path.join(self.trial.data_set.greek_path, figure_file_name)
        self.save_figure(figure_path, format_type)

    def add_figure_title(self):
        figure_title = self.get_greek_figure_title()
        self.fig.suptitle(figure_title)

    def get_greek_figure_title(self):
        data_set = self.trial.data_set.folder_name
        power_string = self.trial.power_obj.power_string
        trial_number = self.trial.trial_number
        plot_title = f"{data_set}, {power_string} dBm, Trial {trial_number}"
        return plot_title

    def file_list_has_data(self, folder_path, file_list):
        for file_name in file_list:
            file_path = os.path.join(folder_path, file_name)
            if self.file_has_data(file_path):
                return True
        return False

    def file_has_data(self, file_path):
        with open(file_path, "r") as file:
            file.readline()
            first_data_line = file.readline()
            has_data = (first_data_line != "")
        return has_data
    
    def get_figure_file_name(self, format_type, name):
        base_figure_file_name = self.get_base_figure_file_name()
        figure_file_name = (f"{name}_{base_figure_file_name}.{format_type}")
        return figure_file_name

    def get_base_figure_file_name(self):
        data_set = self.trial.data_set.folder_name
        power_string = self.trial.power_obj.power_string
        trial_number = self.trial.trial_number
        figure_file_name = (f"{data_set}_{power_string}_dBm_"
                            f"Trial_{trial_number}")
        return figure_file_name
    
    def save_figure(self, figure_path, format_type):
        self.update_figure_size(8, 8)
        plt.savefig(figure_path, bbox_inches='tight', format=format_type)
        plt.close()

    def update_figure_size(self, width=8, height=4.8):
        plt.tight_layout()
        self.fig.set_size_inches(width, height)
        plt.gca().set_position([0, 0, 1, 1])
        self.fig.subplots_adjust(top=0.92)
