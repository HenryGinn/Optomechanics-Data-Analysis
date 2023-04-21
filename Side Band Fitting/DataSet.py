import os
import sys

sys.path.append("..")

from Power import Power
import PutTrialsInFolders
from Features.SpectraRaw import SpectraRaw
from Features.SpectraValid import SpectraValid
from Features.SpectraPeak import SpectraPeak
from Features.AverageSpectra import AverageSpectra
from Features.PlotSpectra import PlotSpectra
from Features.Transmissions import Transmissions
from Features.Greek import Greek
from Features.Greek2 import Greek2
from Features.AverageGreek import AverageGreek
from Utils import make_folder

class DataSet():

    """
    This class handles everything within a data set such as 15112022 or 16112022_overnight.
    Most of the folder structure handling happens here.

    Different data sets have different folder structures.
    For data sets in the same format as 15112022, use folder_structure_type=1
    For data sets in the same format as 16112022_overnight, use folder_structure_type=2
    For data sets in the same format as 19112022, use folder_structure_type=2
    """

    def __init__(self, folder_name, folder_structure_type, data_set_path=None):
        self.folder_name = folder_name
        self.folder_structure_type = folder_structure_type
        self.set_data_set_path_names(data_set_path)
        self.process_power_structures()
        self.setup_data_set()
        
    def set_data_set_path_names(self, data_set_path):
        script_path = sys.path[0]
        script_folder_path = os.path.dirname(script_path)
        self.parent_path = os.path.dirname(script_folder_path)
        self.set_data_set_path(data_set_path)
        self.set_results_paths()

    def set_data_set_path(self, data_set_path):
        if data_set_path is None:
            self.data_set_path = os.path.join(self.parent_path, "Data Sets", self.folder_name)
        else:
            self.data_set_path = os.path.join(data_set_path, self.folder_name)

    def set_results_paths(self):
        self.create_parent_results_folder()
        self.create_data_set_results_folder()

    def create_parent_results_folder(self):
        self.parent_results_path = os.path.join(self.parent_path, "Side Band Results")
        make_folder(self.parent_results_path, message=True)

    def create_data_set_results_folder(self):
        self.results_path = os.path.join(self.parent_results_path, self.folder_name)
        make_folder(self.results_path, message=True)

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

    def set_power_objects(self):
        power_data = zip(self.power_folder_names,
                         self.transmission_folder_paths,
                         self.spectrum_folder_paths)
        self.power_objects = [Power(self, power_folder, transmission_path, spectrum_path)
                              for power_folder, transmission_path, spectrum_path in power_data]

    def set_power_list(self):
        self.power_list = [power_obj.power
                           for power_obj in self.power_objects]

    def setup_data_set(self):
        self.fix_folder_structure()
        self.process_folder_structure()
        self.set_feature_objects()

    def fix_folder_structure(self):
        if self.folder_structure_type == 3:
            PutTrialsInFolders.put_trials_in_folders(self.data_set_path)

    def process_folder_structure(self):
        for power_obj in self.power_objects:
            power_obj.process_power()

    def set_feature_objects(self):
        self.spectra_raw_obj = SpectraRaw(self)
        self.spectra_valid_obj = SpectraValid(self)
        self.spectra_peak_obj = SpectraPeak(self)
        self.average_spectra_obj = AverageSpectra(self)
        self.plot_spectra_obj = PlotSpectra(self)
        self.transmission_obj = Transmissions(self)
        self.greek_obj = Greek(self)
        self.greek_2_obj = Greek2(self)
        self.average_greek_obj = AverageGreek(self)

    def spectra_raw(self, command="Load", **kwargs):
        self.spectra_raw_obj.execute(command, **kwargs)

    def spectra_valid(self, command="Load", **kwargs):
        self.spectra_valid_obj.execute(command, **kwargs)

    def spectra_peak(self, command="Load", **kwargs):
        self.spectra_peak_obj.execute(command, **kwargs)

    def average_spectra(self, command="Load", **kwargs):
        self.average_spectra_obj.execute(command, **kwargs)

    def plot_spectra(self, command="Plot", **kwargs):
        self.plot_spectra_obj.execute(command, **kwargs)

    def transmission(self, command="Load", **kwargs):
        self.transmission_obj.execute(command, **kwargs)

    def greek(self, command="Load", **kwargs):
        self.greek_obj.execute(command, **kwargs)

    def greek_2(self, command="Plot", **kwargs):
        self.greek_2_obj.execute(command, **kwargs)

    def average_greek(self, command="Plot", **kwargs):
        self.average_greek_obj.execute(command, **kwargs)
        
    def __str__(self):
        string = f"{self.folder_name}"
        return string
