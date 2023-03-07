import matplotlib.pyplot as plt
import os
from GreekAxis import GreekAxis
from GammaTrial import GammaTrial
from OmegaTrial import OmegaTrial

class GreekFigure():

    """
    This handles a figure for Omega and Gamma data at the trial level.
    It manages OmegaTrial and GammaTrial objects, and is an interface
    for GreekAxis
    """

    def __init__(self, trial_obj):
        self.trial = trial_obj

    def create_omega_figure(self, format_type):
        self.omega_obj = OmegaTrial(self.trial)
        self.set_omega_children()
        if self.omega_valid():
            self.do_create_omega_figure(format_type)

    def set_omega_children(self):
        self.omega_obj.set_omega_files()
        self.omega_obj.set_omega_children()

    def omega_valid(self):
        omega_non_empty = self.file_list_has_data(self.omega_obj.path, self.omega_obj.omega_files)
        return omega_non_empty

    def do_create_omega_figure(self, format_type):
        self.fig, axis = plt.subplots()
        self.omega_axis = GreekAxis(self, self.omega_obj, axis)
        self.plot_omegas(axis)
        self.add_omega_labels()
        self.save_omega_figure(format_type)

    def plot_omegas(self, axis):
        for omega_child in self.omega_obj.omega_children:
            self.omega_axis.plot_greek_child(omega_child)

    def add_omega_labels(self):
        self.fig.suptitle("Omega")
        self.omega_axis.add_plot_labels()
    
    def save_omega_figure(self, format_type):
        figure_file_name = self.get_omega_figure_file_name(format_type)
        figure_path = os.path.join(self.trial.data_set.omega_path, figure_file_name)
        self.update_figure_size(8, 4.8)
        self.fig.subplots_adjust(top=0.92)
        plt.savefig(figure_path, bbox_inches='tight', format=format_type)
        plt.close()
        

    def create_gamma_figure(self, format_type):
        self.gamma_obj = GammaTrial(self.trial)
        self.set_gamma_children()
        if self.gamma_valid():
            self.do_create_gamma_figure(format_type)

    def set_gamma_children(self):
        self.gamma_obj.set_gamma_files()
        self.gamma_obj.set_gamma_children()

    def gamma_valid(self):
        gamma_non_empty = self.file_list_has_data(self.gamma_obj.path, self.gamma_obj.gamma_files)
        return gamma_non_empty

    def do_create_gamma_figure(self, format_type):
        self.fig, axis = plt.subplots()
        self.gamma_axis = GreekAxis(self, self.gamma_obj, axis)
        self.plot_gammas(axis)
        self.add_gamma_labels()
        self.save_gamma_figure(format_type)

    def plot_gammas(self, axis):
        for gamma_child in self.gamma_obj.gamma_children:
            self.gamma_axis.plot_greek_child(gamma_child)

    def add_gamma_labels(self):
        self.fig.suptitle("Gamma")
        self.gamma_axis.add_plot_labels()
    
    def save_gamma_figure(self, format_type):
        figure_file_name = self.get_gamma_figure_file_name(format_type)
        figure_path = os.path.join(self.trial.data_set.gamma_path, figure_file_name)
        self.update_figure_size(8, 4.8)
        self.fig.subplots_adjust(top=0.92)
        plt.savefig(figure_path, bbox_inches='tight', format=format_type)
        plt.close()

    
    def create_omega_and_gamma_figure(self, format_type):
        self.gamma_obj = GammaTrial(self.trial)
        self.set_gamma_children()
        self.omega_obj = OmegaTrial(self.trial)
        self.set_omega_children()
        if self.omega_and_gamma_valid():
            self.do_create_omega_and_gamma_figure(format_type)

    def omega_and_gamma_valid(self):
        gamma_non_empty = self.file_list_has_data(self.gamma_obj.path, self.gamma_obj.gamma_files)
        return gamma_non_empty

    def do_create_omega_and_gamma_figure(self, format_type):
        self.fig, (axis_omega, axis_gamma) = plt.subplots(2, sharex=True)
        self.omega_axis = GreekAxis(self, self.omega_obj, axis_omega)
        self.gamma_axis = GreekAxis(self, self.gamma_obj, axis_gamma)
        self.plot_omegas(axis_omega)
        self.plot_gammas(axis_gamma)
        self.add_omega_and_gamma_figure_labels()
        self.save_omega_and_gamma_figure(format_type)

    def add_omega_and_gamma_figure_labels(self):
        self.add_omega_and_gamma_titles()
        self.omega_axis.add_y_axis_labels()
        self.gamma_axis.add_y_axis_labels()
        self.gamma_axis.add_x_axis_labels()

    def add_omega_and_gamma_titles(self):
        figure_title = self.get_omega_and_gamma_figure_title()
        self.fig.suptitle(figure_title)

    def get_omega_and_gamma_figure_title(self):
        data_set = self.trial.data_set.folder_name
        power_string = self.trial.power_obj.power_string
        trial_number = self.trial.trial_number
        plot_title = ("Dynamical Backaction\n"
                      f"{data_set}, {power_string} dBm, Trial {trial_number}")
        return plot_title

    def omega_and_gamma_files_valid(self):
        if self.omega_valid():
            if self.gamma_valid():
                return True
        return False

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

    def save_omega_and_gamma_figure(self, format_type):
        figure_file_name = self.get_omega_and_gamma_figure_file_name(format_type)
        figure_path = os.path.join(self.trial.data_set.omega_and_gamma_path, figure_file_name)
        plt.tight_layout()
        plt.savefig(figure_path, bbox_inches='tight', format=format_type)
        plt.close()

    def get_omega_figure_file_name(self, format_type):
        base_figure_file_name = self.get_base_figure_file_name()
        figure_file_name = (f"Omega_{base_figure_file_name}.{format_type}")
        return figure_file_name

    def get_gamma_figure_file_name(self, format_type):
        base_figure_file_name = self.get_base_figure_file_name()
        figure_file_name = (f"Gamma_{base_figure_file_name}.{format_type}")
        return figure_file_name

    def get_omega_and_gamma_figure_file_name(self, format_type):
        base_figure_file_name = self.get_base_figure_file_name()
        figure_file_name = (f"OmegaAndGamma_{base_figure_file_name}.{format_type}")
        return figure_file_name

    def get_base_figure_file_name(self):
        data_set = self.trial.data_set.folder_name
        power_string = self.trial.power_obj.power_string
        trial_number = self.trial.trial_number
        figure_file_name = (f"{data_set}_{power_string}_dBm_"
                            f"Trial_{trial_number}")
        return figure_file_name

    def update_figure_size(self, width=8, height=4.8):
        plt.tight_layout()
        self.fig.set_size_inches(width, height)
        plt.gca().set_position([0, 0, 1, 1])
