from statistics import mean
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
        drifts_and_gammas = [(drift, gamma) for detuning, drift, gamma in file_contents
                             if detuning == self.detuning.detuning]
        drifts, gammas = zip(*drifts_and_gammas)
        self.average_drift = mean(drifts)
        self.average_gamma = mean(gammas)
