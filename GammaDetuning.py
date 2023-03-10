import numpy as np
from AverageDetuning import AverageDetuning

class GreekDetuning():

    def __init__(self, detuning_obj):
        self.detuning = detuning_obj
        self.average_detuning = AverageDetuning(detuning_obj)

    def set__averages(self, average_size):
        self.average_detuning.set_S21_average_objects(average_size)
        for S21_average_obj in self.average_detuning.S21_average_objects:
            S21_average_obj.set_greek()
            self.average_detuning.set_drifts_average(S21_average_obj)

    def save_greek(self, file):
        for S21_average_obj in self.average_detuning.S21_average_objects:
            drift = S21_average_obj.drift
            omega = S21_average_obj.omega
            gamma = S21_average_obj.gamma
            amplitude = S21_average_obj.amplitude
            file.writelines(f"{self.detuning.detuning}\t{drift}\t{omega}\t{gamma}\t{amplitude}\n")
        return file

    def set_average_greek(self, file_contents):
        drifts, greeks = self.get_drifts_and_greeks(file_contents)
        if drifts is not None:
            self.set_greek_average_data(drifts, greeks)
        else:
            self.average_greek = None

    def get_drifts_and_greeks(self, file_contents):
        drifts_and_greeks = [(drift, greek) for detuning, drift, greek in file_contents
                             if detuning == self.detuning.detuning]
        drifts, greeks = self.process_drifts_and_greeks(drifts_and_greeks)
        return drifts, greeks

    def process_drifts_and_greeks(self, drifts_and_greeks):
        if drifts_and_greeks != []:
            drifts, greeks = zip(*drifts_and_greeks)
        else:
            drifts, greeks = None, None
        return drifts, greeks

    def set_greek_average_data(self, drifts, greeks):
        self.average_drift = np.mean(drifts)
        self.average_greek = np.mean(greeks)
        self.deviation = np.std(greeks)
