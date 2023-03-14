import os

import matplotlib.pyplot as plt

from GreekAxis import GreekAxis
from GreekTrial import GreekTrial

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
        self.fig, (axis_omega, axis_gamma, axis_amplitude) = plt.subplots(3, sharex=True)
        self.plot_greeks(axis_omega, axis_gamma, axis_amplitude)
        self.add_greek_figure_labels()
        self.save_greek_figure(format_type)

    def plot_greeks(self, axis_omega, axis_gamma, axis_amplitude):
        self.create_greek_axes(axis_omega, axis_gamma, axis_amplitude)
        self.fit_greek_axes()
        self.plot_greek_axes()

    def create_greek_axes(self, axis_omega, axis_gamma, axis_amplitude):
        self.create_omega_axis(axis_omega)
        self.create_gamma_axis(axis_gamma)
        self.create_amplitude_axis(axis_amplitude)
        self.greek_axes = [self.omega_axis, self.gamma_axis, self.amplitude_axis]

    def create_omega_axis(self, axis):
        self.omega_axis = GreekAxis(self.trial, self.greek_obj.omega_children, axis)
        self.omega_axis.name = "Omega"
        self.omega_axis.name_latex = "$\Omega_m$"
        self.omega_axis.units = "Hz"

    def create_gamma_axis(self, axis):
        self.gamma_axis = GreekAxis(self.trial, self.greek_obj.gamma_children, axis)
        self.gamma_axis.name = "Gamma"
        self.gamma_axis.name_latex = "$\Gamma_m$"
        self.gamma_axis.units = "Hz"

    def create_amplitude_axis(self, axis):
        self.amplitude_axis = GreekAxis(self.trial, self.greek_obj.amplitude_children, axis)
        self.amplitude_axis.name = "Amplitude"
        self.amplitude_axis.name_latex = "Amplitude"
        self.amplitude_axis.units = "dBm"

    def fit_greek_axes(self):
        for greek_axis in self.greek_axes:
            for greek_child in greek_axis.greek_children:
                greek_child.fit_curve()

    def plot_greek_axes(self):
        for greek_axis in self.greek_axes:
            greek_axis.plot_children()

    def add_greek_figure_labels(self):
        self.add_figure_title()
        self.add_y_axis_labels()
        self.amplitude_axis.add_x_axis_labels()

    def add_y_axis_labels(self):
        self.omega_axis.add_y_axis_labels()
        self.gamma_axis.add_y_axis_labels()
        self.amplitude_axis.add_y_axis_labels()
    
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
