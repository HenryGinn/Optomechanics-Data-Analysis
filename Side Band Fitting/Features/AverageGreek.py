import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from DataFit import DataFit
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path
from Utils import get_moving_average

class AverageGreek(Feature):

    name = "Average of Omega and Gamma"

    def __init__(self, data_set_obj):
        Feature.__init__(self, data_set_obj)
        self.set_commands()
    
    def set_paths(self):
        self.set_folder_path()
        for power_obj in self.data_set_obj.power_objects:
            self.set_power_path(power_obj)
            self.set_trial_paths(power_obj)

    def set_power_path(self, power_obj):
        path = os.path.join(self.folder_path, power_obj.power_string)
        power_obj.average_greek_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.average_greek_path, f"Trial {trial_obj.trial_number}.txt")
        trial_obj.average_greek_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.greek_2("Load")

    def save_data_set_obj(self, data_set_obj):
        for power_obj in data_set_obj.power_objects:
            self.save_power_obj(power_obj)

    def save_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_obj(trial_obj)
            self.save_trial_obj(trial_obj)

    def set_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            values = self.get_values_from_detuning_obj(detuning_obj)
            self.set_detuning_obj(detuning_obj, values)

    def set_detuning_obj(self, detuning_obj, values):
        if len(values) > 0:
            self.set_detuning_obj_non_trivial(detuning_obj, values)
        else:
            self.set_detuning_obj_trivial(detuning_obj)

    def set_detuning_obj_non_trivial(self, detuning_obj, values):
        detuning_obj.gamma = np.median(values[0])
        detuning_obj.omega = np.abs(np.median(values[1]))
        detuning_obj.amplitude = np.median(values[2])

    def set_detuning_obj_trivial(self, detuning_obj):
        detuning_obj.gamma = None
        detuning_obj.omega = None
        detuning_obj.amplitude = None

    def get_values_from_detuning_obj(self, detuning_obj):
        values = [(spectrum_obj.gamma, spectrum_obj.omega, spectrum_obj.amplitude)
                  for spectrum_obj in detuning_obj.spectrum_objects
                  if spectrum_obj.gamma is not None]
        return list(zip(*values))

    def save_trial_obj(self, trial_obj):
        with open(trial_obj.average_greek_path, "w") as file:
            file.writelines("Detuning (Hz)\tGamma\tOmega\tAmplitude\n")
            self.save_trial_obj_to_file(trial_obj, file)

    def save_trial_obj_to_file(self, trial_obj, file):
        for detuning_obj in trial_obj.detuning_objects:
            if detuning_obj.gamma is not None:
                self.save_detuning_obj_to_file(detuning_obj, file)

    def save_detuning_obj_to_file(self, detuning_obj, file):
        detuning = detuning_obj.detuning
        gamma = detuning_obj.gamma
        omega = detuning_obj.omega
        amplitude = detuning_obj.amplitude
        file.writelines(f"{detuning}\t{gamma}\t{omega}\t{amplitude}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(trial_obj.average_greek_path)
                       for power_obj in self.data_set_obj.power_objects
                       for trial_obj in power_obj.trial_objects])

    def do_load_data(self):
        for power_obj in self.data_set_obj.power_objects:
            self.load_power_obj(power_obj)

    def load_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.load_trial_obj(trial_obj)

    def load_trial_obj(self, trial_obj):
        file_contents = get_file_contents_from_path(trial_obj.average_greek_path)
        detunings, gammas, omegas, amplitudes = file_contents
        for detuning_obj in trial_obj.detuning_objects:
            if detuning_obj.detuning in detunings:
                index = list(detunings).index(detuning_obj.detuning)
                detuning_obj.gamma = gammas[index]
                detuning_obj.omega = omegas[index]
                detuning_obj.amplitude = amplitudes[index]
            else:
                detuning_obj.gamma = None
                detuning_obj.omega = None
                detuning_obj.amplitude = None

    def create_plots(self):
        for power_obj in self.data_set_obj.power_objects:
            for trial_obj in power_obj.trial_objects:
                self.create_trial_plot(trial_obj)

    def create_trial_plot(self, trial_obj):
        lines_objects = self.get_lines_objects(trial_obj)
        plots_obj = Plots(lines_objects)
        plots_obj.parent_results_path, _ = os.path.split(trial_obj.average_greek_path)
        plots_obj.title = str(trial_obj)
        plots_obj.plot()

    def get_lines_objects(self, trial_obj):
        values = list(zip(*[(detuning_obj.detuning, detuning_obj.gamma, detuning_obj.omega, detuning_obj.amplitude)
                            for detuning_obj in trial_obj.detuning_objects
                            if detuning_obj.gamma is not None]))
        line_objects = [Line(values[0], values_list) for values_list in values[1:]]
        lines_objects = [Lines([line_obj]) for line_obj in line_objects]
        return lines_objects
