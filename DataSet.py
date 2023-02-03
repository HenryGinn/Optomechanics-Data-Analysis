import os
import sys
from Power import Power

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
        self.data_set_path = os.path.join(self.parent_path, self.folder_name)

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
                              for power_folder, transmission_path, spectrum_path in power_data]

    def set_power_list(self):
        self.power_list = [power_obj.power
                           for power_obj in self.power_objects]

    def output_power_list(self):
        print("\nPower list")
        for power in self.power_list:
            print(power)

    def process_power_folders(self):
        for power_obj in self.power_objects:
            power_obj.process_power()

    def __str__(self):
        string = (f"Folder name: {self.folder_name}\n" + 
                  f"Folder structure type: {self.folder_structure_type}\n" +
                  f"Data set path: {self.data_set_path}\n"
                  f"Repository folder: {self.repository_path}\n" +
                  f"Parent folder: {self.parent_path}\n")
        return string
