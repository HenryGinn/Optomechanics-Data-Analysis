import sys
import os

from Drift import Drift

class DataSet():

    def __init__(self, folder_name):
        self.folder_name = folder_name
        self.setup_data_set()

    def setup_data_set(self):
        self.set_paths()
        self.make_results_folders()
        self.set_drift_objects()

    def set_paths(self):
        script_path = sys.path[0]
        repo_path = os.path.dirname(script_path)
        self.parent_path = os.path.dirname(repo_path)
        self.path = os.path.join(self.parent_path, "Data Sets", self.folder_name)
    
    def make_results_folders(self):
        self.make_parent_results_folder()
        self.make_data_set_results_folder()

    def make_parent_results_folder(self):
        self.parent_results_path = os.path.join(self.parent_path, "Frequency Comb Results")
        if not os.path.isdir(self.parent_results_path):
            print(f"Making 'Frequency Comb Results' folder at {self.parent_results_path}")
            os.mkdir(self.parent_results_path)

    def make_data_set_results_folder(self):
        self.results_path = os.path.join(self.parent_results_path, self.folder_name)
        if not os.path.isdir(self.results_path):
            print(f"Making results folder at {self.results_path}")
            os.mkdir(self.results_path)

    def set_drift_objects(self):
        self.drift_objects = [Drift(self, folder_name)
                              for folder_name in os.listdir(self.path)]
        
    def process_spectrum(self):
        for drift_obj in self.drift_objects:
            drift_obj.process_spectrum()

    def __str__(self):
        string = f"Data Set {self.folder_name}"
        return string