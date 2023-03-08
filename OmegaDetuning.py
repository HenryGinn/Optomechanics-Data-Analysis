import numpy as np
from AverageDetuning import AverageDetuning
from Utils import *

class OmegaDetuning():

    def __init__(self, detuning_obj):
        self.detuning = detuning_obj
        self.average_detuning = AverageDetuning(detuning_obj)
    
    def set_omegas_all(self):
        if self.detuning.valid:
            self.do_set_omegas_all()
        else:
            self.omegas, self.drifts = None, None

    def do_set_omegas_all(self):
        centre_frequencies = self.detuning.spectrum_centre_frequencies
        omegas_all = centre_frequencies - self.detuning.cavity_frequency - self.detuning.detuning
        acceptable_indexes = get_acceptable_indexes(omegas_all)
        self.detuning.spectrum_indexes = self.detuning.spectrum_indexes[acceptable_indexes]
        self.omegas = omegas_all[acceptable_indexes]
        self.drifts = self.average_detuning.get_drifts(self.detuning.spectrum_indexes, len(self.detuning.spectrum_objects))

    def set_omegas_averages(self, average_size):
        drifts_all, omegas_all = self.get_omegas_all_from_file()
        if drifts_all is None:
            self.omegas, self.drifts, self.deviations = None, None, None
        else:
            self.do_set_omegas_averages(drifts_all, omegas_all, average_size)

    def do_set_omegas_averages(self, drifts_all, omegas_all, average_size):
        average_size = self.average_detuning.get_average_size(average_size, len(omegas_all))
        self.omegas = self.average_detuning.average_list(omegas_all, average_size)
        self.drifts = self.average_detuning.average_list(drifts_all, average_size)
        self.deviations = self.average_detuning.get_standard_deviations(omegas_all, average_size)

    def get_omegas_all_from_file(self):
        with open(self.detuning.trial.omega_all.path, "r") as file:
            file.readline()
            file_contents = [[float(value) for value in line.strip().split("\t")]
                              for line in file]
            drifts, omegas = self.get_drift_and_omega_from_file(file_contents)
        return drifts, omegas

    def get_drift_and_omega_from_file(self, file_contents):
        drifts_and_omegas = [(drift, omega) for detuning, drift, omega in file_contents
                             if detuning == self.detuning.detuning]
        drifts, omegas = self.get_drifts_and_omegas_from_tuples(drifts_and_omegas)
        return drifts, omegas

    def get_drifts_and_omegas_from_tuples(self, drifts_and_omegas):
        if len(drifts_and_omegas) != 0:
            drifts, omegas = self.do_get_drifts_and_omegas_from_tuples(drifts_and_omegas)
        else:
            drifts, omegas = None, None
        return drifts, omegas

    def do_get_drifts_and_omegas_from_tuples(self, drifts_and_omegas):
        drifts, omegas = zip(*drifts_and_omegas)
        drifts = np.array(drifts)
        omegas = np.array(omegas)
        return drifts, omegas
