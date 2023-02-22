import numpy as np
import os
from Trial import Trial
from OmegaTrial import OmegaTrial
from GammaTrial import GammaTrial
from TrialPlot import TrialPlot

class Power():

    """
    This class handles all the data for a specific power within one dataset.
    Organising the processing of the trials and plotting things happens here.

    Folder structure "A" is where there is only one trial for a given power.
    Folder structure "B" is where there are multiple
    15112022 and 16112022_overnight are of type A and 19112022 is of type B
    """
    
    def __init__(self, data_set, power_folder, transmission_path, spectrum_path):
        self.data_set = data_set
        self.folder_name = power_folder
        self.transmission_path = transmission_path
        self.spectrum_path = spectrum_path
        self.set_power_from_folder_name()

    def set_power_from_folder_name(self):
        try:
            self.power_string = self.folder_name[0:2]
            self.power = self.process_power_string()
        except:
            raise Exception(f"Power could not be read from folder name: {folder_name}")

    def process_power_string(self):
        power_dB = round(float(self.power_string), 1)
        power_mW = (10**(power_dB/10))/1000
        return power_mW

    def process_power(self):
        self.set_trial_paths()
        self.set_trial_objects()

    def set_trial_paths(self):
        set_trial_path_functions = {1: self.set_trial_paths_A,
                                    2: self.set_trial_paths_A,
                                    3: self.set_trial_paths_B}
        set_trial_path_functions[self.data_set.folder_structure_type]()

    def set_trial_paths_A(self):
        self.trial_transmission_paths = [self.transmission_path]
        self.trial_spectrum_paths = [self.spectrum_path]

    def set_trial_paths_B(self):
        self.set_trial_transmission_paths_B()
        self.set_trial_spectrum_paths_B()

    def set_trial_transmission_paths_B(self):
        trial_transmission_folder_names = list(sorted(os.listdir(self.transmission_path)))
        self.trial_transmission_paths = [os.path.join(self.transmission_path, folder_name)
                                         for folder_name in trial_transmission_folder_names]

    def set_trial_spectrum_paths_B(self):
        trial_spectrum_folder_names = list(sorted(os.listdir(self.spectrum_path)))
        self.trial_spectrum_paths = [os.path.join(self.spectrum_path, folder_name)
                                     for folder_name in trial_spectrum_folder_names]

    def set_trial_objects(self):
        trial_paths_data = zip(self.trial_transmission_paths,
                               self.trial_spectrum_paths)
        self.trial_objects = [Trial(self, trial_number, trial_transmission_path, trial_spectrum_path)
                              for trial_number, (trial_transmission_path, trial_spectrum_path)
                              in enumerate(trial_paths_data)]

    def process_transmission(self):
        for trial_obj in self.trial_objects:
            trial_obj.process_transmission()

    def process_S21(self):
        for trial_obj in self.trial_objects:
            trial_obj.process_S21()

    def create_omega_objects(self):
        self.omega_objects = [OmegaTrial(trial_obj)
                              for trial_obj in self.trial_objects]

    def process_omega(self):
        for omega_obj in self.omega_objects:
            omega_obj.process_omega_all()

    def average_omega(self, average_size):
        for omega_obj in self.omega_objects:
            omega_obj.omega_average(average_size)

    def create_gamma_objects(self):
        self.gamma_objects = [GammaTrial(trial_obj)
                              for trial_obj in self.trial_objects]

    def process_gamma(self, average_size):
        for gamma_obj in self.gamma_objects:
            gamma_obj.process_gamma(average_size)
            gamma_obj.save_gamma(average_size)

    def create_trial_plots(self, plot_name):
        for trial_obj in self.trial_objects:
            trial_plot_obj = TrialPlot(trial_obj)
            trial_plot_obj.create_trial_plots(plot_name)

    def create_detuning_plots(self, plot_name):
        for trial_obj in self.trial_objects:
            trial_plot_obj = TrialPlot(trial_obj)
            trial_plot_obj.create_detuning_plots(plot_name)

    def output_trial_paths(self):
        self.output_trial_transmission_paths()
        self.output_trial_spectrum_path()

    def output_trial_transmission_paths(self):
        print("\nTrial transmission paths")
        for path in self.trial_transmission_paths:
            print(path)

    def output_trial_spectrum_paths(self):
        print("\nTrial spectrum paths")
        for path in self.trial_spectrum_paths:
            print(path)

    def output_trials_information(self):
        print("\nTrials information")
        for trial in self.trial_objects:
            print(trial)

    def __str__(self):
        string = (f"Data set: {self.data_set.folder_name}\n"
                  f"Folder name: {self.folder_name}\n"
                  f"Transmission path: {self.transmission_path}\n"
                  f"Spectrum path: {self.spectrum_path}\n"
                  f"Power: {self.power}\n")
        return string
