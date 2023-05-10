import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path
from Utils import evaluate_lorentzian

class FitHeuristic(Feature):

    name = "Fit Heuristic"

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
        power_obj.fit_heuristic_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)
            self.set_detuning_paths(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.fit_heuristic_path, f"Trial {trial_obj.trial_number}")
        trial_obj.fit_heuristic_path = path
        make_folder(path)

    def set_detuning_paths(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.trial_obj.fit_heuristic_path, f"{detuning_obj.detuning} Hz.txt")
        detuning_obj.fit_heuristic_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.spectra_fit("Load")

    def save_data_set_obj(self, data_set_obj):
        for power_obj in data_set_obj.power_objects:
            self.save_power_obj(power_obj)

    def save_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.save_trial_obj(trial_obj)

    def save_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_obj(detuning_obj)
            self.save_detuning_obj(detuning_obj)

    def set_detuning_obj(self, detuning_obj):
        for spectrum_obj in detuning_obj.spectrum_objects:
            self.set_spectrum_obj(spectrum_obj)

    def set_spectrum_obj(self, spectrum_obj):
        if spectrum_obj.has_valid_peak:
            self.do_set_spectrum_obj(spectrum_obj)
        else:
            spectrum_obj.fit_heuristic = None

    def do_set_spectrum_obj(self, spectrum_obj):
        spectrum_obj.load_S21()
        data = spectrum_obj.S21
        fit_values = evaluate_lorentzian(spectrum_obj.frequency,
                                         spectrum_obj.fitting_parameters)
        spectrum_obj.fit_heuristic = np.mean((data - fit_values)**2)

    def save_detuning_obj(self, detuning_obj):
        with open(detuning_obj.fit_heuristic_path, "w") as file:
            file.writelines("Spectrum Index\tFit Heuristic\n")
            self.save_detuning_obj_to_file(detuning_obj, file)

    def save_detuning_obj_to_file(self, detuning_obj, file):
        for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
            if spectrum_obj.has_valid_peak:
                self.save_spectrum_obj_to_file(spectrum_obj, index, file)

    def save_spectrum_obj_to_file(self, spectrum_obj, index, file):
        fit_heuristic = spectrum_obj.fit_heuristic
        file.writelines(f"{index}\t{fit_heuristic}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.fit_heuristic_path)
                       for power_obj in self.data_set_obj.power_objects
                       for trial_obj in power_obj.trial_objects
                       for detuning_obj in trial_obj.detuning_objects])

    def do_load_data(self):
        for power_obj in self.data_set_obj.power_objects:
            self.load_power_obj(power_obj)

    def load_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.load_trial_obj(trial_obj)

    def load_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.load_detuning_obj(detuning_obj)

    def load_detuning_obj(self, detuning_obj):
        file_contents = get_file_contents_from_path(detuning_obj.fit_heuristic_path)
        if len(file_contents) > 0:
            indices, fit_heuristics = file_contents
            for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
                if index in indices:
                    list_index = list(indices).index(index)
                    spectrum_obj.has_valid_peak = True
                    spectrum_obj.fit_heuristic = fit_heuristics[list_index]
                else:
                    spectrum_obj.has_valid_peak = False
                    spectrum_obj.fit_heuristic = None

    def create_plots(self, **kwargs):
        for power_obj in self.data_set_obj.power_objects:
            for trial_obj in power_obj.trial_objects:
                self.create_trial_plot(trial_obj, **kwargs)

    def create_trial_plot(self, trial_obj, **kwargs):
        lines_objects = self.get_lines_objects(trial_obj)
        plots_obj = Plots(lines_objects, **kwargs)
        plots_obj.parent_results_path, _ = os.path.split(trial_obj.fit_heuristic_path)
        plots_obj.title = str(trial_obj)
        plots_obj.plot()

    def get_lines_objects(self, trial_obj):
        lines_objects = [self.get_lines_obj(detuning_obj)
                         for detuning_obj in trial_obj.detuning_objects]
        return lines_objects

    def get_lines_obj(self, detuning_obj):
        line_objects = [self.get_line_obj_S21(detuning_obj)]
        lines_obj = Lines(line_objects)
        lines_obj.title = detuning_obj.detuning
        return lines_obj
    
    def get_line_obj_S21(self, detuning_obj):
        values = [(spectrum_obj.index, spectrum_obj.fit_heuristic) for spectrum_obj in detuning_obj.spectrum_objects
                    if spectrum_obj.fit_heuristic is not None]
        x_values, y_values = zip(*values)
        line_obj = Line(x_values, y_values)
        return line_obj
