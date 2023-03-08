import matplotlib.pyplot as plt
import os
from GreekAxis import GreekAxis
from GammaTrial import GammaTrial
from OmegaTrial import OmegaTrial

class GreekFigure():

    """
    This handles a figure involving Omega or Gamma data at the trial level.
    It manages OmegaTrial and GammaTrial objects, and is an interface
    for GreekAxis.
    """

    def __init__(self, trial_obj):
        self.trial = trial_obj

    def create_omega_figure(self, format_type):
        self.set_omega_obj()
        if self.omega_files_valid():
            self.do_create_omega_figure(format_type)

    def set_omega_obj(self):
        self.omega_obj = OmegaTrial(self.trial)
        self.omega_obj.set_omega_children()

    def omega_files_valid(self):
        omega_non_empty = self.file_list_has_data(self.omega_obj.path, self.omega_obj.files)
        return omega_non_empty

    def do_create_omega_figure(self, format_type):
        self.fig, axis_omega = plt.subplots()
        self.plot_omega(axis_omega)
        self.add_omega_labels()
        self.save_omega_figure(format_type)

    def plot_omega(self, axis):
        self.omega_axis = GreekAxis(self, self.omega_obj, axis)
        self.plot_greeks(self.omega_obj, self.omega_axis)

    def add_omega_labels(self):
        self.fig.suptitle("Omega")
        self.omega_axis.add_plot_labels()
    
    def save_omega_figure(self, format_type):
        figure_file_name = self.get_figure_file_name(format_type, "Omega")
        figure_path = os.path.join(self.trial.data_set.omega_path, figure_file_name)
        self.save_figure(figure_path, format_type)
        

    def create_gamma_figure(self, format_type):
        self.set_gamma_obj()
        if self.gamma_files_valid():
            self.do_create_gamma_figure(format_type)

    def set_gamma_obj(self):
        self.gamma_obj = GammaTrial(self.trial)
        self.gamma_obj.set_gamma_children()

    def gamma_files_valid(self):
        gamma_non_empty = self.file_list_has_data(self.gamma_obj.path, self.gamma_obj.files)
        return gamma_non_empty

    def do_create_gamma_figure(self, format_type):
        self.fig, axis_gamma = plt.subplots()
        self.plot_gamma(axis_gamma)
        self.add_gamma_labels()
        self.save_gamma_figure(format_type)
        
    def plot_gamma(self, axis):
        self.gamma_axis = GreekAxis(self, self.gamma_obj, axis)
        self.plot_greeks(self.gamma_obj, self.gamma_axis)

    def add_gamma_labels(self):
        self.fig.suptitle("Gamma")
        self.gamma_axis.add_plot_labels()
    
    def save_gamma_figure(self, format_type):
        figure_file_name = self.get_figure_file_name(format_type, "Gamma")
        figure_path = os.path.join(self.trial.data_set.gamma_path, figure_file_name)
        self.save_figure(figure_path, format_type)

    
    def create_omega_and_gamma_figure(self, format_type):
        self.set_omega_obj()
        self.set_gamma_obj()
        if self.omega_and_gamma_files_valid():
            self.do_create_omega_and_gamma_figure(format_type)

    def omega_and_gamma_files_valid(self):
        if self.omega_files_valid():
            if self.gamma_files_valid():
                return True
        return False

    def do_create_omega_and_gamma_figure(self, format_type):
        self.fig, (axis_omega, axis_gamma) = plt.subplots(2, sharex=True)
        self.plot_omega(axis_omega)
        self.plot_gamma(axis_gamma)
        self.add_omega_and_gamma_figure_labels()
        self.save_omega_and_gamma_figure(format_type)

    def add_omega_and_gamma_figure_labels(self):
        self.add_omega_and_gamma_title()
        self.omega_axis.add_y_axis_labels()
        self.gamma_axis.add_y_axis_labels()
        self.gamma_axis.add_x_axis_labels()

    def add_omega_and_gamma_title(self):
        figure_title = self.get_omega_and_gamma_figure_title()
        self.fig.suptitle(figure_title)

    def get_omega_and_gamma_figure_title(self):
        data_set = self.trial.data_set.folder_name
        power_string = self.trial.power_obj.power_string
        trial_number = self.trial.trial_number
        plot_title = f"{data_set}, {power_string} dBm, Trial {trial_number}"
        return plot_title

    def save_omega_and_gamma_figure(self, format_type):
        figure_file_name = self.get_figure_file_name(format_type, "OmegaAndGamma")
        figure_path = os.path.join(self.trial.data_set.omega_and_gamma_path, figure_file_name)
        self.save_figure(figure_path, format_type)

    def plot_greeks(self, greek_obj, axis):
        for greek_child in greek_obj.children:
            axis.plot_greek_child(greek_child)

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
        self.update_figure_size(8, 4.8)
        plt.savefig(figure_path, bbox_inches='tight', format=format_type)
        plt.close()

    def update_figure_size(self, width=8, height=4.8):
        plt.tight_layout()
        self.fig.set_size_inches(width, height)
        plt.gca().set_position([0, 0, 1, 1])
        self.fig.subplots_adjust(top=0.92)
