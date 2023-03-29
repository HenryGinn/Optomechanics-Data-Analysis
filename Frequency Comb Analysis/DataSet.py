import sys
import os

from Drift import Drift
from AlignSpectra import AlignSpectra
from AverageGroups import AverageGroups
from NoiseThreshold import NoiseThreshold
from PeakCoordinates import PeakCoordinates
from PeakFits import PeakFits
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
        self.set_feature_objects()

    def set_paths(self):
        repo_path = os.path.dirname(self.script_path)
        self.parent_path = os.path.dirname(repo_path)
        self.path = os.path.join(self.parent_path, "Data Sets", self.folder_name)
    
    def make_results_folders(self):
        self.make_parent_results_folder()
        self.make_data_set_results_folder()

    def make_parent_results_folder(self):
        self.parent_results_path = os.path.join(self.parent_path, "Frequency Comb Results")
        make_folder(self.parent_results_path, message=True)

    def make_data_set_results_folder(self):
        self.results_path = os.path.join(self.parent_results_path, self.folder_name)
        make_folder(self.results_path, message=True)

    def set_drift_objects(self):
        self.drift_objects = [Drift(self, folder_name)
                              for folder_name in os.listdir(self.path)]
        self.drift_objects = sorted(self.drift_objects, key=lambda x: x.drift_value)
        self.drift_objects = get_sliced_list(self.drift_objects, self.drift_indexes)

    def set_feature_objects(self):
        self.align_spectra_obj = AlignSpectra(self)
        self.average_groups_obj = AverageGroups(self)
        self.noise_threshold_obj = NoiseThreshold(self)
        self.peak_coordinates_obj = PeakCoordinates(self)
        self.peak_fits_obj = PeakFits(self)
        self.envelope_trends_obj = EnvelopeTrends(self)
        self.peak_gaps_obj = PeakGaps(self)
    
    def plot_spectra(self, subplots=None, drifts=None, detunings=None,
                     groups=None, noise=False, markers=False, fit=False):
        drift_objects = get_sliced_list(self.drift_objects, drifts)
        for drift_obj in drift_objects:
            drift_obj.plot_spectra(subplots, detunings, groups, noise, markers, fit)

    def plot_peak_fits(self, groups=None, legend=True):
        for drift_obj in self.drift_objects:
            drift_obj.plot_peak_fits(groups, legend)

    def align_spectra(self, command="Load"):
        self.align_spectra_obj.execute(command)

    def average_groups(self, command="Load"):
        self.average_groups_obj.execute(command)

    def noise_threshold(self, command="Load"):
        self.noise_threshold_obj.execute(command)

    def peak_coordinates(self, command="Load"):
        self.peak_coordinates_obj.execute(command)

    def peak_fits(self, command="Load"):
        self.peak_fits_obj.execute(command)

    def envelope_trends(self, command="Plot"):
        self.envelope_trends_obj.execute(command)

    def peak_gaps(self, command="Plot"):
        self.average_groups_obj.execute("Load")
        self.peak_gaps_obj.execute(command)
    
    def __str__(self):
        string = f"Data Set {self.folder_name}"
        return string
