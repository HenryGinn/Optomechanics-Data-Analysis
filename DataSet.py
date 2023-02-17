import os
import sys
from Power import Power
import PutTrialsInFolders
import PlotGammaAndOmega

class DataSet():

    """
    This class handles everything within a data set such as 15112022 or 16112022_overnight.
    Most of the folder structure handling happens here.

    Different data sets have different folder structures.
    For data sets in the same format as 15112022, use folder_structure_type=1
    For data sets in the same format as 16112022_overnight, use folder_structure_type=2
    For data sets in the same format as 19112022, use folder_structure_type=2
    """

    def __init__(self, folder_name, folder_structure_type):
        self.folder_name = folder_name
        self.folder_structure_type = folder_structure_type
        self.set_data_set_path_names()
        self.process_power_structures()
        
    def set_data_set_path_names(self):
        script_path = sys.path[0]
        self.repository_path = os.path.dirname(script_path)
        self.parent_path = os.path.dirname(self.repository_path)
        self.data_set_path = os.path.join(self.parent_path, "Data Sets", self.folder_name)

    def process_power_structures(self):
        self.set_power_folder_path_data()
        self.set_power_objects()
        self.set_power_list()

    def set_power_folder_path_data(self):
        if self.folder_structure_type == 1:
            self.set_power_folder_path_data_1()
        elif self.folder_structure_type in [2, 3]:
            self.set_power_folder_path_data_2()
        else:
            raise Exception("Folder structure type unknown. Must be 1, 2, or 3")

    def set_power_folder_path_data_1(self):
        self.power_folder_names = sorted(list(os.listdir(self.data_set_path)))
        self.set_transmission_folder_paths_1()
        self.set_spectrum_folder_paths_1()

    def set_transmission_folder_paths_1(self):
        self.transmission_folder_paths = [os.path.join(self.data_set_path,
                                                       power_folder_name,
                                                       "Transmission")
                                          for power_folder_name in self.power_folder_names]

    def set_spectrum_folder_paths_1(self):
        self.spectrum_folder_paths = [os.path.join(self.data_set_path,
                                                   power_folder_name,
                                                   "Spectrum")
                                      for power_folder_name in self.power_folder_names]

    def set_power_folder_path_data_2(self):
        self.set_transmission_folder_paths_2()
        self.set_spectrum_folder_paths_2()

    def set_transmission_folder_paths_2(self):
        transmission_folder_path = os.path.join(self.data_set_path, "Transmission")
        self.power_folder_names = sorted(list(os.listdir(transmission_folder_path)))
        self.transmission_folder_paths = [os.path.join(transmission_folder_path, name)
                                          for name in self.power_folder_names]

    def set_spectrum_folder_paths_2(self):
        spectrum_folder_path = os.path.join(self.data_set_path, "Spectrum")
        self.spectrum_folder_paths = [os.path.join(spectrum_folder_path, name)
                                      for name in self.power_folder_names]

    def output_power_folder_names(self):
        print("\nPower folder names")
        for name in self.power_folder_names:
            print(name)

    def output_transmission_folder_paths(self):
        print("\nTransmission folder paths")
        for path in self.transmission_folder_paths:
            print(path)

    def output_spectrum_folder_paths(self):
        print("\nSpectrum folder paths")
        for path in self.spectrum_folder_paths:
            print(path)

    def set_power_objects(self):
        power_data = zip(self.power_folder_names,
                         self.transmission_folder_paths,
                         self.spectrum_folder_paths)
        self.power_objects = [Power(self, power_folder, transmission_path, spectrum_path)
                              for power_folder, transmission_path, spectrum_path in power_data][1:2]

    def set_power_list(self):
        self.power_list = [power_obj.power
                           for power_obj in self.power_objects]

    def output_power_list(self):
        print("\nPower list")
        for power in self.power_list:
            print(power)

    def process_folders(self):
        self.fix_folder_structure()
        self.process_folder_structure()
        self.create_results_folders()

    def fix_folder_structure(self):
        if self.folder_structure_type == 3:
            PutTrialsInFolders.put_trials_in_folders(self.folder_name)

    def process_folder_structure(self):
        for power_obj in self.power_objects:
            power_obj.process_power()
    
    def create_results_folders(self):
        self.create_data_set_results_folder()
        self.create_S21_folder()
        self.create_omega_folder()
        self.create_gamma_folder()
    
    def create_results_folder(self):
        self.results_path = os.path.join(self.parent_path, "Results")
        if os.path.isdir(self.results_path) == False:
            os.mkdir(self.results_path)

    def create_S21_folder(self):
        self.S21_path = os.path.join(self.data_set_results_path, "S21 Peaks")
        if os.path.isdir(self.S21_path) == False:
            os.mkdir(self.S21_path)

    def create_omega_folder(self):
        self.omega_path = os.path.join(self.data_set_results_path, "Omega Results")
        if os.path.isdir(self.omega_path) == False:
            os.mkdir(self.omega_path)

    def create_gamma_folder(self):
        self.gamma_path = os.path.join(self.data_set_results_path, "Gamma Results")
        if os.path.isdir(self.gamma_path) == False:
            os.mkdir(self.gamma_path)

    def average_omega(self, average_size = None):
        if self.omega_folder_exists():
            for power_obj in self.power_objects:
                power_obj.average_omega(average_size)

    def omega_folder_exists(self):
        if hasattr(self, "omega_path"):
            return True
        else:
            raise Exception(("Omega folder does not exist\n"
                             "Run process_omega method first"))

    def process_transmission(self):
        for power_obj in self.power_objects:
            print(f"Processing transmission: {power_obj.folder_name}")
            power_obj.process_transmission()

    def process_S21(self):
        for power_obj in self.power_objects:
            print(f"Processing S21: {power_obj.folder_name}")
            power_obj.process_S21()

    def process_omega(self):
        for power_obj in self.power_objects:
            print(f"Finding omega: {power_obj.folder_name}")
            power_obj.process_omega()
        
    def process_gamma(self):
        for power_obj in self.power_objects:
            print(f"Finding gamma: {power_obj.folder_name}")
            power_obj.process_gamma()

    def save_gamma(self):
        self.create_gamma_folder()
        for power_obj in self.power_objects:
            power_obj.save_gamma()

    def create_data_set_results_folder(self):
        self.create_results_folder()
        self.data_set_results_path = os.path.join(self.results_path, self.folder_name)
        if os.path.isdir(self.data_set_results_path) == False:
            os.mkdir(self.data_set_results_path)

    def create_trial_plots(self, plot_name):
        for power_obj in self.power_objects:
            power_obj.create_trial_plots(plot_name)

    def create_detuning_plots(self, plot_name):
        for power_obj in self.power_objects:
            power_obj.create_detuning_plots(plot_name)

    def plot_omega(self, format_type="pdf"):
        PlotGammaAndOmega.generate_plot("Omega",
                                        self.omega_path,
                                        format_type)

    def plot_gamma(self, format_type="pdf"):
        PlotGammaAndOmega.generate_plot("Gamma",
                                        self.gamma_path,
                                        format_type)

    def __str__(self):
        string = (f"Folder name: {self.folder_name}\n" + 
                  f"Folder structure type: {self.folder_structure_type}\n" +
                  f"Data set path: {self.data_set_path}\n"
                  f"Repository folder: {self.repository_path}\n" +
                  f"Parent folder: {self.parent_path}\n")
        return string
