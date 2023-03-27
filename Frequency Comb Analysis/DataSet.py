import sys
import os

from Drift import Drift
from EnvelopeTrends import EnvelopeTrends
from PeakGaps import PeakGaps
from Utils import get_sliced_list
from Utils import make_folder

class DataSet():

    def __init__(self, folder_name, script_path=None, drifts=None, detunings=None):
        self.folder_name = folder_name
        self.set_script_path(script_path)
        self.drift_indexes = drifts
        self.detuning_indexes = detunings
        self.setup_data_set()

    def set_script_path(self, script_path):
        if script_path is None:
            self.script_path = sys.path[0]
        else:
            self.script_path = script_path

    def setup_data_set(self):
        self.set_paths()
        self.make_results_folders()
        self.set_drift_objects()
        self.set_aligned_spectra_paths()
        self.set_feature_objects()

    def set_paths(self):
        repo_path = os.path.dirname(self.script_path)
        self.parent_path = os.path.dirname(repo_path)
        self.path = os.path.join(self.parent_path, "Data Sets", self.folder_name)
    
    def make_results_folders(self):
        self.make_parent_results_folder()
        self.make_data_set_results_folder()
        self.make_noise_threshold_folder()
        self.make_peak_coordinates_folder()
        self.make_peak_fitting_folder()

    def make_parent_results_folder(self):
        self.parent_results_path = os.path.join(self.parent_path, "Frequency Comb Results")
        make_folder(self.parent_results_path, message=True)

    def make_data_set_results_folder(self):
        self.results_path = os.path.join(self.parent_results_path, self.folder_name)
        make_folder(self.results_path, message=True)

    def make_noise_threshold_folder(self):
        self.noise_threshold_path = os.path.join(self.results_path, "Noise Threshold")
        make_folder(self.noise_threshold_path, message=True)

    def make_peak_coordinates_folder(self):
        self.peak_coordinates_path = os.path.join(self.results_path, "Peak Coordinates")
        make_folder(self.peak_coordinates_path, message=True)

    def make_peak_fitting_folder(self):
        self.peak_fit_path = os.path.join(self.results_path, "Peak Fitting")
        make_folder(self.peak_fit_path, message=True)

    def set_drift_objects(self):
        self.drift_objects = [Drift(self, folder_name)
                              for folder_name in os.listdir(self.path)]
        self.drift_objects = sorted(self.drift_objects, key=lambda x: x.drift_value)
        self.drift_objects = get_sliced_list(self.drift_objects, self.drift_indexes)

    def set_aligned_spectra_paths(self):
        self.make_aligned_spectra_folder()
        for drift_obj in self.drift_objects:
            drift_obj.create_aligned_spectra_folder()
            drift_obj.populate_aligned_spectra_folder()

    def make_aligned_spectra_folder(self):
        self.aligned_spectra_path = os.path.join(self.results_path, "Aligned Spectra")
        make_folder(self.aligned_spectra_path, message=True)
        
    def set_aligned_spectra(self, drifts=None, detunings=None):
        drift_objects = get_sliced_list(self.drift_objects, drifts)
        for drift_obj in drift_objects:
            drift_obj.set_aligned_spectra(detunings)

    def set_feature_objects(self):
        self.envelope_trends_obj = EnvelopeTrends(self)
        self.peak_gaps_obj = PeakGaps(self)

    def load_aligned_spectra(self):
        print("Loading aligned spectra")
        for drift_obj in self.drift_objects:
            drift_obj.load_aligned_spectra()

    def save_noise_threshold(self):
        self.set_noise_threshold_paths()
        for drift_obj in self.drift_objects:
            drift_obj.save_noise_threshold()

    def load_noise_threshold(self):
        print("Loading noise threshold")
        self.set_noise_threshold_paths()
        for drift_obj in self.drift_objects:
            drift_obj.load_noise_threshold()

    def set_noise_threshold_paths(self):
        for drift_obj in self.drift_objects:
            drift_obj.set_noise_threshold_paths()

    def save_peak_coordinates(self, drifts=None, detunings=None):
        drift_objects = get_sliced_list(self.drift_objects, drifts)
        self.set_peak_coordinates_paths()
        for drift_obj in drift_objects:
            drift_obj.save_peak_coordinates(detunings)

    def load_peak_coordinates(self):
        print("Loading peak coordinates")
        self.set_peak_coordinates_paths()
        for drift_obj in self.drift_objects:
            drift_obj.load_peak_coordinates()

    def set_peak_coordinates_paths(self):
        for drift_obj in self.drift_objects:
            drift_obj.set_peak_coordinates_paths()

    def save_peak_fits(self):
        self.set_peak_fit_paths()
        for drift_obj in self.drift_objects:
            drift_obj.save_peak_fits()

    def load_peak_fits(self):
        self.set_peak_fit_paths()
        for drift_obj in self.drift_objects:
            drift_obj.load_peak_fits()

    def set_peak_fit_paths(self):
        for drift_obj in self.drift_objects:
            drift_obj.set_peak_fit_path()
    
    def plot_spectra(self, subplots=None, drifts=None, detunings=None,
                     groups=None, noise=False, markers=False, fit=False):
        drift_objects = get_sliced_list(self.drift_objects, drifts)
        for drift_obj in drift_objects:
            drift_obj.plot_spectra(subplots, detunings, groups, noise, markers, fit)

    def plot_peak_fits(self, groups=None, legend=True):
        for drift_obj in self.drift_objects:
            drift_obj.plot_peak_fits(groups, legend)

    def envelope_trends(self, command="Plot"):
        self.envelope_trends_obj.execute(command)

    def peak_gaps(self, command="Plot"):
        self.peak_gaps_obj.execute(command)
    
    def __str__(self):
        string = f"Data Set {self.folder_name}"
        return string
