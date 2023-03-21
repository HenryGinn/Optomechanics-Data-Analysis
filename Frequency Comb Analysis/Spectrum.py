import numpy as np

from Data import Data
from Utils import get_modified_deviation
from Utils import flatten

class Spectrum(Data):

    noise_deviations_threshold = 3
    peak_index_proximity = 100

    def __init__(self, group_obj):
        self.group_obj = group_obj
    
    def initialise_from_path(self, path):
        Data.__init__(self, self.group_obj, path)

    def set_peak_coordinates(self):
        non_noise_indices = self.get_non_noise_indices()
        close_to_indices = self.get_close_to_indices(non_noise_indices)
        self.set_peak_clusters(non_noise_indices, close_to_indices)
        self.set_peak_indices()

    def get_non_noise_indices(self):
        _, modified_deviation = get_modified_deviation(self.S21)
        noise = np.median(self.S21) + self.noise_deviations_threshold * modified_deviation
        non_noise_indices = np.nonzero(self.S21 > noise)[0]
        return non_noise_indices

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

    def set_peak_indices(self):
        self.peak_indices = [max(cluster_indices, key=lambda x: self.S21[x])
                             for cluster_indices in self.peak_clusters]
