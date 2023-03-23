import numpy as np

from Data import Data
from Utils import get_modified_deviation

class Spectrum(Data):

    window_width = 10
    peak_index_proximity = 100
    noise_multiplier_threshold = 3.5

    def __init__(self, group_obj):
        self.group_obj = group_obj
    
    def initialise_from_path(self, path):
        Data.__init__(self, self.group_obj, path)

    def set_noise_threshold(self):
        self.noise_threshold = [self.get_noise_threshold(index)
                                for index in range(len(self.S21))]

    def get_noise_threshold(self, index):
        S21_within_window = self.get_S21_within_window(index)
        noise_threshold = np.median(S21_within_window) * self.noise_multiplier_threshold
        return noise_threshold

    def get_S21_within_window(self, index):
        left_index = max(0, index - self.window_width)
        right_index = min(len(self.S21) - 1, index + self.window_width)
        S21_within_window = np.minimum(self.S21, 10**-11)[left_index:right_index]
        return S21_within_window

    def set_peak_coordinates(self):
        non_noise_indices = np.nonzero(self.S21 > self.noise_threshold)[0]
        close_to_indices = self.get_close_to_indices(non_noise_indices)
        self.set_peak_clusters(non_noise_indices, close_to_indices)
        self.set_peak_values()

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

    def set_peak_clusters(self, non_noise_indices, close_to_indices):
        self.peak_clusters = [set([non_noise_indices[0]])]
        for index in non_noise_indices:
            close_indices = close_to_indices[index]
            self.add_indices_to_peak_clusters(index, close_indices)

    def add_indices_to_peak_clusters(self, index, close_indices):
        if self.indices_already_in_cluster(index, close_indices):
            self.peak_clusters[-1] = self.peak_clusters[-1].union(close_indices)
        else:
            self.peak_clusters.append(close_indices)

    def indices_already_in_cluster(self, index, close_indices):
        previous_cluster = self.peak_clusters[-1]
        intersection = previous_cluster.intersection(close_indices)
        intersection_non_empty = (len(intersection) != 0)
        return intersection_non_empty

    def set_peak_values(self):
        self.peak_indices = [max(cluster_indices, key=lambda x: self.S21[x])
                             for cluster_indices in self.peak_clusters]
        self.peak_frequencies = self.frequency[self.peak_indices]
        self.peak_S21s = self.S21[self.peak_indices]
