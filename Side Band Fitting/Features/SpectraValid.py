import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path
from Utils import get_moving_average

class SpectraValid(Feature):

    name = "Spectra Valid"
    peak_ratio_threshold = 2.5#11.5
    reject_first_n = 0
    window = 5

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
        power_obj.spectra_valid_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)
            self.set_detuning_paths(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.spectra_valid_path, f"Trial {trial_obj.trial_number}")
        trial_obj.spectra_valid_path = path
        make_folder(path)

    def set_detuning_paths(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            detuning_obj.spectra_valid_path = os.path.join(trial_obj.spectra_valid_path,
                                                     f"{detuning_obj.detuning} Hz.txt")

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
        spectra_count = len(detuning_obj.spectrum_objects)
        if spectra_count < 10:
            self.set_detuning_process_all(detuning_obj)
        else:
            self.set_detuning_skip_first_few(detuning_obj)

    def set_detuning_process_all(self, detuning_obj):
        for spectrum_obj in detuning_obj.spectrum_objects:
            self.set_spectrum_peak_validity(spectrum_obj)

    def set_detuning_skip_first_few(self, detuning_obj):
        for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
            if index >= self.reject_first_n:
                self.set_spectrum_peak_validity(spectrum_obj)
            else:
                spectrum_obj.has_valid_peak = False

    def set_spectrum_peak_validity(self, spectrum_obj):
        #spectrum_obj.load_S21()
        #S21 = get_moving_average(spectrum_obj.S21, self.window)
        #S21 = spectrum_obj.S21
        #peak = np.max(S21)
        #noise = np.median(S21)
        #peak_ratio = peak / noise
        #spectrum_obj.has_valid_peak = (peak_ratio > self.peak_ratio_threshold)
        spectrum_obj.has_valid_peak = True

    def save_detuning_obj(self, detuning_obj):
        with open(detuning_obj.spectra_valid_path, "w") as file:
            file.writelines("Spectrum index\tValid\n")
            self.save_detuning_obj_to_file(detuning_obj, file)

    def save_detuning_obj_to_file(self, detuning_obj, file):
        for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
            file.writelines(f"{index}\t{int(spectrum_obj.has_valid_peak)}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.spectra_valid_path)
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
        _, valid_array = get_file_contents_from_path(detuning_obj.spectra_valid_path)
        for spectrum_obj, valid in zip(detuning_obj.spectrum_objects, valid_array):
            spectrum_obj.has_valid_peak = bool(valid)

    def create_plots(self, **kwargs):
        for power_obj in self.data_set_obj.power_objects:
            for trial_obj in power_obj.trial_objects:
                for detuning_obj in trial_obj.detuning_objects:
                    self.create_detuning_plots(detuning_obj, **kwargs)

    def create_detuning_plots(self, detuning_obj, **kwargs):
        lines_objects = [self.get_lines_obj(spectrum_obj)
                         for spectrum_obj in detuning_obj.spectrum_objects]
        plots_obj = Plots(lines_objects, **kwargs)
        plots_obj.parent_results_path, _ = os.path.split(detuning_obj.spectra_valid_path)
        plots_obj.title = str(detuning_obj)
        plots_obj.plot()

    def get_lines_obj(self, spectrum_obj):
        line_objects = [self.get_line_obj(spectrum_obj)]
        lines_obj = Lines(line_objects)
        return lines_obj

    def get_line_obj(self, spectrum_obj):
        spectrum_obj.load_S21()
        x_values = spectrum_obj.frequency
        y_values = get_moving_average(spectrum_obj.S21, self.window)
        colour = self.get_colour(spectrum_obj)
        line_obj = Line(x_values, y_values, colour=colour)
        return line_obj

    def get_colour(self, spectrum_obj):
        if spectrum_obj.has_valid_peak:
            return "b"
        else:
            return "r"
