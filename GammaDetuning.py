import numpy as np
from AverageDetuning import AverageDetuning

class GammaDetuning():

    def __init__(self, detuning_obj):
        self.detuning = detuning_obj
        self.average_detuning = AverageDetuning(detuning_obj)

    def set_gamma_averages(self, average_size):
        self.average_detuning.set_S21_average_objects(average_size)
        for S21_average_obj in self.average_detuning.S21_average_objects:
            S21_average_obj.set_gamma()
            self.average_detuning.set_drifts_average(S21_average_obj)

    def save_gamma(self, file):
        for S21_average_obj in self.average_detuning.S21_average_objects:
            drift = S21_average_obj.drift
            gamma = S21_average_obj.gamma
            file.writelines(f"{self.detuning.detuning}\t{drift}\t{gamma}\n")
        return file

    def set_average_gamma(self, file_contents):
        drifts, gammas = self.get_drifts_and_gammas(file_contents)
        if drifts is not None:
            self.set_gamma_average_data(drifts, gammas)
        else:
            self.average_gamma = None

    def get_drifts_and_gammas(self, file_contents):
        drifts_and_gammas = [(drift, gamma) for detuning, drift, gamma in file_contents
                             if detuning == self.detuning.detuning]
        drifts, gammas = self.process_drifts_and_gammas(drifts_and_gammas)
        return drifts, gammas

    def process_drifts_and_gammas(self, drifts_and_gammas):
        if drifts_and_gammas != []:
            drifts, gammas = zip(*drifts_and_gammas)
        else:
            drifts, gammas = None, None
        return drifts, gammas

    def set_gamma_average_data(self, drifts, gammas):
        self.average_drift = np.mean(drifts)
        self.average_gamma = np.mean(gammas)
        self.deviation = np.std(gammas)
