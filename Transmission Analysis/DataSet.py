import sys
import os

from SubDataSet import SubDataSet

class DataSet():

    def __init__(self, folder_name, folder_structure_type):
        self.folder_name = folder_name
        self.folder_structure_type = folder_structure_type
        self.setup_data_set()

    def setup_data_set(self):
        self.set_paths()
        self.make_results_folders()
        self.create_sub_data_sets()
        self.set_power_objects()

    def set_paths(self):
        script_path = sys.path[0]
        repo_path = os.path.dirname(script_path)
        self.parent_path = os.path.dirname(repo_path)
        self.main_data_set_path = os.path.join(self.parent_path, "Data Sets", self.folder_name, "Transmission")

    def create_sub_data_sets(self):
        self.set_sub_data_sets_functions()
        self.sub_data_sets_functions[self.folder_structure_type]()

    def set_sub_data_sets_functions(self):
        self.sub_data_sets_functions = {1: self.set_sub_data_sets_1,
                                        2: self.set_sub_data_sets_2}

    def set_sub_data_sets_1(self):
        self.sub_data_sets = [SubDataSet(self, self.main_data_set_path, "Data")]

    def set_sub_data_sets_2(self):
        self.sub_data_sets = [SubDataSet(self,
                                         os.path.join(self.main_data_set_path, folder_name),
                                         folder_name)
                              for folder_name in os.listdir(self.main_data_set_path)]

    def make_results_folders(self):
        self.make_parent_results_folder()
        self.make_data_set_results_folder()

    def make_parent_results_folder(self):
        self.parent_results_path = os.path.join(self.parent_path, "Transmission Results")
        if not os.path.isdir(self.parent_results_path):
            print(f"Making 'Transmission Results' folder at {self.parent_results_path}")
            os.mkdir(self.parent_results_path)

    def make_data_set_results_folder(self):
        self.results_path = os.path.join(self.parent_results_path, self.folder_name)
        if not os.path.isdir(self.results_path):
            print(f"Making results folder at {self.results_path}")
            os.mkdir(self.results_path)

    def set_power_objects(self):
        for sub_data_set in self.sub_data_sets:
            sub_data_set.set_power_objects()

    def read_raw_transmission(self):
        for sub_data_set in self.sub_data_sets:
            sub_data_set.read_raw_transmission()

    def plot_transmission(self, option="Raw", group_size=None, subplots=None):
        for sub_data_set in self.sub_data_sets:
            sub_data_set.plot_transmission(option, group_size, subplots)

    def align_transmission(self, group_size=None):
        for sub_data_set in self.sub_data_sets:
            sub_data_set.align_transmission(group_size)
