import os

import numpy as np

from CombFunction import CombFunction
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_file_contents_from_path

class PeakCoordinates(CombFunction):

    name = "Peak Coordinates"
    peak_index_proximity = 100

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        self.set_folder_path()
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)
            self.set_detuning_paths(drift_obj)

    def set_drift_path(self, drift_obj):
        path = os.path.join(self.folder_path, drift_obj.folder_name)
        drift_obj.peak_coordinates_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            path = os.path.join(drift_obj.peak_coordinates_path,
                                f"{detuning_obj.detuning} Hz")
            detuning_obj.peak_coordinates_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.align_spectra("Load")
        self.data_set_obj.average_groups("Load")
        self.data_set_obj.noise_threshold("Load")

    def save_data_set_obj(self, data_set_obj):
        for drift_obj in self.data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.save_detuning_obj(detuning_obj)

    def save_detuning_obj(self, detuning_obj):
        self.set_peak_coordinates(detuning_obj.spectrum_obj)
        self.save_peak_coordinates(detuning_obj)

    def set_peak_coordinates(self, spectrum_obj):
        non_noise_indices = np.nonzero(spectrum_obj.S21 > spectrum_obj.noise_threshold)[0]
        close_to_indices = self.get_close_to_indices(non_noise_indices)
        self.set_peak_clusters(spectrum_obj, non_noise_indices, close_to_indices)
        self.set_peak_values(spectrum_obj)

    def get_close_to_indices(self, non_noise_indices):
        close_to_indices = {index_outer: self.get_close_to_index(index_outer, non_noise_indices)
                            for index_outer in non_noise_indices}
        return close_to_indices

    def get_close_to_index(self, index_outer, non_noise_indices):
        close_to_index = set([index_inner for index_inner in non_noise_indices
                              if self.index_near(index_inner, index_outer)])
        return close_to_index

    def index_near(self, index_inner, index_outer):
        proximity = abs(index_inner - index_outer)
        is_near = (proximity < self.peak_index_proximity)
        return is_near

    def set_peak_clusters(self, spectrum_obj, non_noise_indices, close_to_indices):
        spectrum_obj.peak_clusters = [set([non_noise_indices[0]])]
        for index in non_noise_indices:
            close_indices = close_to_indices[index]
            self.add_indices_to_peak_clusters(spectrum_obj, index, close_indices)

    def add_indices_to_peak_clusters(self, spectrum_obj, index, close_indices):
        if self.indices_already_in_cluster(spectrum_obj, index, close_indices):
            spectrum_obj.peak_clusters[-1] = spectrum_obj.peak_clusters[-1].union(close_indices)
        else:
            spectrum_obj.peak_clusters.append(close_indices)

    def indices_already_in_cluster(self, spectrum_obj, index, close_indices):
        previous_cluster = spectrum_obj.peak_clusters[-1]
        intersection = previous_cluster.intersection(close_indices)
        intersection_non_empty = (len(intersection) != 0)
        return intersection_non_empty

    def set_peak_values(self, spectrum_obj):
        spectrum_obj.peak_indices = [max(cluster_indices, key=lambda x: spectrum_obj.S21[x])
                                     for cluster_indices in spectrum_obj.peak_clusters]
        spectrum_obj.peak_frequencies = spectrum_obj.frequency[spectrum_obj.peak_indices]
        spectrum_obj.peak_S21s = spectrum_obj.S21[spectrum_obj.peak_indices]

    def save_peak_coordinates(self, detuning_obj):
        with open(detuning_obj.peak_coordinates_path, "w") as file:
            file.writelines("Index\tFrequency (Hz)\tS21 (mW)\n")
            self.save_peak_coordinates_to_file(detuning_obj.spectrum_obj, file)

    def save_peak_coordinates_to_file(self, spectrum_obj, file):
        for peak_index in spectrum_obj.peak_indices:
            frequency = spectrum_obj.frequency[peak_index]
            S21 = spectrum_obj.S21[peak_index]
            file.writelines(f"{peak_index}\t{frequency}\t{S21}\n")


    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.peak_coordinates_path)
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects])

    def do_load_data(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.load_drift_obj(drift_obj)

    def load_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.load_detuning_obj(detuning_obj)

    def load_detuning_obj(self, detuning_obj):
        self.create_spectrum_obj(detuning_obj)
        file_contents = self.get_file_contents(detuning_obj)
        spectrum_obj = detuning_obj.spectrum_obj
        self.set_peak_coordinates_from_file_contents(spectrum_obj, file_contents)

    def create_spectrum_obj(self, detuning_obj):
        if not hasattr(detuning_obj, "spectrum_obj"):
            detuning_obj.spectrum_obj = Spectrum(self)

    def get_file_contents(self, detuning_obj):
        path = detuning_obj.peak_coordinates_path
        file_contents = get_file_contents_from_path(path)
        return file_contents

    def set_peak_coordinates_from_file_contents(self, spectrum_obj, file_contents):
        (spectrum_obj.peak_indices,
         spectrum_obj.peak_frequencies,
         spectrum_obj.peak_S21s) = file_contents

