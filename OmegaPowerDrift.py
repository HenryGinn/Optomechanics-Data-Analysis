import numpy as np
import matplotlib.pyplot as plt
from AverageDetuning import AverageDetuning
from AverageData import AverageData
from DataFit import DataFit
from Utils import get_file_contents

class OmegaPowerDrift():

    def __init__(self, data_set):
        self.data_set = data_set

    def plot_drift(self):
        self.average_spectra()
        self.average_trials()
        self.create_plot()

    def average_spectra(self):
        for power_obj in self.data_set.power_objects:
            for trial_obj in power_obj.trial_objects:
                self.set_detuning_0_averages(trial_obj)

    def set_detuning_0_averages(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            if float(detuning_obj.detuning) == float(0):
                self.set_detuning_0_average(trial_obj, detuning_obj)

    def set_detuning_0_average(self, trial_obj, detuning_obj):
        self.prepare_trial(trial_obj, detuning_obj)
        self.find_detuning_0_average(trial_obj, detuning_obj)

    def prepare_trial(self, trial_obj, detuning_obj):
        trial_obj.set_spectrum_file_path()
        spectrum_file_contents = get_file_contents(trial_obj.spectrum_file_path)
        detuning_obj.extract_spectrum_from_file_detuning(spectrum_file_contents)

    def find_detuning_0_average(self, trial_obj, detuning_obj):
        detuning_0_average_obj = AverageDetuning(detuning_obj)
        detuning_0_average_obj.set_S21_average_objects()
        trial_obj.detuning_0_average = detuning_0_average_obj.S21_average_objects[0]

    def average_trials(self):
        for power_obj in self.data_set.power_objects:
            self.average_trials_power(power_obj)

    def average_trials_power(self, power_obj):
        self.detuning_0_included = False
        if hasattr(power_obj.trial_objects[0], "detuning_0_average"):
            power_obj.average_trial = power_obj.trial_objects[0].detuning_0_average
            power_obj.average_trial.plot_S21()
            self.detuning_0_included = True
        
    def create_plot(self):
        if self.detuning_0_included:
            plt.figure()
            for power_obj in self.data_set.power_objects:
                if hasattr(power_obj, "average_trial"):
                    plot_obj = DataFit(power_obj.average_trial)
                    plt.plot(plot_obj.data.frequency, plot_obj.data.S21, '.', alpha = 1, label=power_obj.power_string)
            plot_obj.set_x_ticks_and_labels()
            plt.xlabel(f'Frequency ({plot_obj.prefix})')
            plt.ylabel('Amplitude')
            plt.title("Average 0 Detuning Spectra\nFor Several Powers")
            plt.legend(bbox_to_anchor=(1.05, 1), loc = 2)
            plt.show()
        else:
            print("0 detuning was not included in this data set")
        
