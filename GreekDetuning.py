import numpy as np
from AverageDetuning import AverageDetuning

class GreekDetuning():

    def __init__(self, detuning_obj):
        self.detuning = detuning_obj
        self.average_detuning = AverageDetuning(detuning_obj)

    def set_greeks(self, average_size):
        self.average_detuning.set_S21_average_objects(average_size)
        for S21_average_obj in self.average_detuning.S21_average_objects:
            S21_average_obj.set_greeks()
            self.average_detuning.set_drifts_average(S21_average_obj)

    def save_greeks(self, file):
        for S21_average_obj in self.average_detuning.S21_average_objects:
            drift = S21_average_obj.drift
            omega = S21_average_obj.omega
            gamma = S21_average_obj.gamma
            amplitude = S21_average_obj.amplitude
            file.writelines(f"{self.detuning.detuning}\t{drift}\t{omega}\t{gamma}\t{amplitude}\n")
        return file

    def set_greek_averages(self, file_contents):
        self.set_drifts_and_greeks(file_contents)
        if self.drifts is not None:
            self.do_set_greek_averages()
        else:
            self.average_greek = None

    def set_drifts_and_greeks(self, file_contents):
        drifts_and_greeks = [(drift, omega, gamma, amplitude)
                             for detuning, drift, omega, gamma, amplitude in file_contents
                             if detuning == self.detuning.detuning]
        self.process_drifts_and_greeks(drifts_and_greeks)

    def process_drifts_and_greeks(self, drifts_and_greeks):
        if drifts_and_greeks != []:
            self.drifts, self.omega, self.gamma, self.amplitude = zip(*drifts_and_greeks)
        else:
            self.drifts, self.omega, self.gamma, self.amplitude = None, None, None, None

    def do_set_greek_averages(self):
        self.drift_average = np.mean(self.drifts)
        self.set_greek_average_values()
        self.set_greek_average_deviations()

    def set_greek_average_values(self):
        self.omega_average = np.mean(self.omega)
        self.gamma_average = np.mean(self.gamma)
        self.amplitude_average = np.mean(self.amplitude)

    def set_greek_average_deviations(self):
        self.omega_deviation = np.std(self.omega)
        self.gamma_deviation = np.std(self.gamma)
        self.amplitude_deviation = np.std(self.amplitude)
