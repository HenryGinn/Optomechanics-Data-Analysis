import sys
import os

from Drift import Drift

from SpectraPeak import SpectraPeak
from AlignSpectra import AlignSpectra
from AverageGroups import AverageGroups
from NoiseThreshold import NoiseThreshold
from PeakCoordinates import PeakCoordinates
from PeakCount import PeakCount
from PeakGaps import PeakGaps
from PeakFits import PeakFits
from EnvelopeVertices import EnvelopeVertices
from ReverseFourierTransform import ReverseFourierTransform
from PlotSpectra import PlotSpectra

from Utils import get_sliced_list
from Utils import make_folder

class DataSet():

    def __init__(self, folder_name,
                 script_path=None, data_set_path=None,
                 drifts=None, detunings=None):
        self.folder_name = folder_name
        self.set_script_path(script_path)
        self.drift_indexes = drifts
        self.detuning_indexes = detunings
        self.setup_data_set(data_set_path)

    def set_script_path(self, script_path):
        if script_path is None:
            self.script_path = sys.path[0]
        else:
            self.script_path = script_path

    def setup_data_set(self, data_set_path):
        self.set_paths(data_set_path)
        self.make_results_folders()
        self.set_drift_objects()
        self.set_feature_objects()

    def set_paths(self, data_set_path):
        repo_path = os.path.dirname(self.script_path)
        self.parent_path = os.path.dirname(repo_path)
        self.set_data_set_path(data_set_path)

    def set_data_set_path(self, data_set_path):
        if data_set_path is None:
            self.path = os.path.join(self.parent_path, "Data Sets", self.folder_name)
        else:
            self.path = os.path.join(data_set_path, self.folder_name)
    
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
        self.spectra_peak_obj = SpectraPeak(self)
        self.align_spectra_obj = AlignSpectra(self)
        self.average_groups_obj = AverageGroups(self)
        self.noise_threshold_obj = NoiseThreshold(self)
        self.peak_coordinates_obj = PeakCoordinates(self)
        self.peak_count_obj = PeakCount(self)
        self.peak_gaps_obj = PeakGaps(self)
        self.peak_fits_obj = PeakFits(self)
        self.envelope_vertices_obj = EnvelopeVertices(self)
        self.reverse_fourier_transform_obj = ReverseFourierTransform(self)
        self.plot_spectra_obj = PlotSpectra(self)

    def spectra_peaks(self, command="Load", **kwargs):
        self.spectra_peak_obj.execute(command, **kwargs)

    def align_spectra(self, command="Load", **kwargs):
        self.align_spectra_obj.execute(command, **kwargs)

    def average_groups(self, command="Load", **kwargs):
        self.average_groups_obj.execute(command, **kwargs)

    def noise_threshold(self, command="Load", **kwargs):
        self.noise_threshold_obj.execute(command, **kwargs)

    def peak_coordinates(self, command="Load", **kwargs):
        self.peak_coordinates_obj.execute(command, **kwargs)

    def peak_count(self, command="Plot", **kwargs):
        self.peak_count_obj.execute(command, **kwargs)

    def peak_gaps(self, command="Plot", **kwargs):
        self.peak_gaps_obj.execute(command, **kwargs)

    def peak_fits(self, command="Plot", **kwargs):
        self.peak_fits_obj.execute(command, **kwargs)

    def envelope_vertices(self, command="Plot", **kwargs):
        self.envelope_vertices_obj.execute(command, **kwargs)

    def reverse_fourier_transform(self, command="Plot", **kwargs):
        self.reverse_fourier_transform_obj.execute(command, **kwargs)

    def plot_spectra(self, **kwargs):
        self.plot_spectra_obj.plot(**kwargs)
    
    def __str__(self):
        string = f"Data Set {self.folder_name}"
        return string
