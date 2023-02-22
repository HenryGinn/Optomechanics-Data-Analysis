import numpy as np

class OmegaDetuning():

    def __init__(self, detuning_obj):
        self.detuning = detuning_obj
    
    def get_omegas_all(self):
        centre_frequencies = self.detuning.spectrum_centre_frequencies
        omegas_all = centre_frequencies - self.detuning.cavity_frequency - self.detuning.detuning
        acceptable_indexes = self.detuning.get_acceptable_indexes(omegas_all)
        self.detuning.spectrum_indexes = self.detuning.spectrum_indexes[acceptable_indexes]
        omegas_all = omegas_all[acceptable_indexes]
        drifts = self.detuning.get_drifts(self.detuning.spectrum_indexes, len(self.detuning.spectrum_objects))
        return omegas_all, drifts

    def get_omegas_averages(self, average_size):
        drifts_all, omegas_all = self.get_omegas_all_from_file()
        average_size = self.detuning.get_average_size(average_size, len(omegas_all))
        omegas_averages = self.detuning.average_list(omegas_all, average_size)
        drifts_averages = self.detuning.average_list(drifts_all, average_size)
        return omegas_averages, drifts_averages

    def get_omegas_all_from_file(self):
        with open(self.detuning.trial.omega_all_file_path, "r") as file:
            file.readline()
            file_contents = [[float(value) for value in line.strip().split("\t")]
                              for line in file]
            drifts, omegas = self.get_drift_and_omega_from_file(file_contents)
        return drifts, omegas

    def get_drift_and_omega_from_file(self, file_contents):
        drifts_and_omegas = [(drift, omega) for detuning, drift, omega in file_contents
                             if detuning == self.detuning.detuning]
        drifts, omegas = zip(*drifts_and_omegas)
        drifts = np.array(drifts)
        omegas = np.array(omegas)
        return drifts, omegas
