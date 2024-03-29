import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Features.GetFittingParameters import get_fitting_parameters
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path
from Utils import evaluate_lorentzian
from Utils import get_moving_average

class SpectraFit(Feature):

    name = "Spectra Fit"
    width = 150

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
        power_obj.spectra_fit_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)
            self.set_detuning_paths(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.spectra_fit_path, f"Trial {trial_obj.trial_number}")
        trial_obj.spectra_fit_path = path
        make_folder(path)

    def set_detuning_paths(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.trial_obj.spectra_fit_path, f"{detuning_obj.detuning} Hz.txt")
        detuning_obj.spectra_fit_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.spectra_valid("Load")

    def refresh_data(self):
        self.data_set_obj.spectra_valid("Refresh")

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
            spectrum_obj.fitting_parameters = None

    def do_set_spectrum_obj(self, spectrum_obj):
        spectrum_obj.load_S21()
        spectrum_obj.fitting_parameters = get_fitting_parameters(spectrum_obj)
        spectrum_obj.has_valid_peak = (spectrum_obj.fitting_parameters is not None)

    def save_detuning_obj(self, detuning_obj):
        with open(detuning_obj.spectra_fit_path, "w") as file:
            file.writelines("Spectrum Index\tF\tGamma\tNoise\tResonant\n")
            self.save_detuning_obj_to_file(detuning_obj, file)

    def save_detuning_obj_to_file(self, detuning_obj, file):
        for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
            if spectrum_obj.has_valid_peak:
                self.save_spectrum_obj_to_file(spectrum_obj, index, file)

    def save_spectrum_obj_to_file(self, spectrum_obj, index, file):
        F, gamma, noise, resonant = spectrum_obj.fitting_parameters
        file.writelines(f"{index}\t{F}\t{gamma}\t{noise}\t{resonant}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.spectra_fit_path)
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
        file_contents = get_file_contents_from_path(detuning_obj.spectra_fit_path)
        if len(file_contents) > 0:
            indices, *fitting_parameters = file_contents
            fitting_parameters = list(zip(*fitting_parameters))
            for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
                if index in indices:
                    list_index = list(indices).index(index)
                    spectrum_obj.has_valid_peak = True
                    spectrum_obj.fitting_parameters = fitting_parameters[list_index]
                else:
                    spectrum_obj.has_valid_peak = False
                    spectrum_obj.fitting_parameters = None
        else:
            for spectrum_obj in detuning_obj.spectrum_objects:
                spectrum_obj.has_valid_peak = False
                spectrum_obj.fitting_parameters = None

    def create_plots(self, **kwargs):
        self.process_kwargs(**kwargs)
        for power_obj in self.data_set_obj.power_objects:
            for trial_obj in power_obj.trial_objects:
                for detuning_obj in trial_obj.detuning_objects:
                    self.create_detuning_plot(detuning_obj, **kwargs)

    def process_kwargs(self, **kwargs):
        if "width" in kwargs:
            self.width = kwargs["width"]

    def create_detuning_plot(self, detuning_obj, **kwargs):
        lines_objects = self.get_lines_objects(detuning_obj)
        plots_obj = Plots(lines_objects, **kwargs)
        plots_obj.parent_results_path, _ = os.path.split(detuning_obj.spectra_fit_path)
        plots_obj.title = str(detuning_obj)
        plots_obj.plot()

    def get_lines_objects(self, detuning_obj):
        lines_objects = [self.get_lines_obj(spectrum_obj)
                         for spectrum_obj in detuning_obj.spectrum_objects]
        return lines_objects

    def get_lines_obj(self, spectrum_obj):
        self.set_spectrum_plotting_data(spectrum_obj)
        line_objects = [self.get_line_obj_S21(spectrum_obj)]
        line_objects = self.add_fit_line(spectrum_obj, line_objects)
        lines_obj = Lines(line_objects)
        lines_obj.title = spectrum_obj.index
        return lines_obj

    def set_spectrum_plotting_data(self, spectrum_obj):
        spectrum_obj.load_S21()
        spectrum_obj.S21 = get_moving_average(spectrum_obj.S21, spectrum_obj.moving_average_size)
        if self.width is not None:
            peak_index = np.argmax(spectrum_obj.S21)
            left_index = peak_index - self.width
            right_index = peak_index + self.width
            spectrum_obj.plotting_indices = self.get_plotting_indicies_from_limits(left_index, right_index)
        else:
            spectrum_obj.plotting_indices = slice(None)

    def get_plotting_indicies_from_limits(self, left_index, right_index):
        if left_index >= 0 and right_index <= 5001:
            return slice(left_index, right_index)
        else:
            return slice(None)
    
    def get_line_obj_S21(self, spectrum_obj):
        x_values = spectrum_obj.frequency[spectrum_obj.plotting_indices]
        y_values = spectrum_obj.S21[spectrum_obj.plotting_indices]
        y_values = get_moving_average(y_values, spectrum_obj.moving_average_size)
        line_obj = Line(x_values, y_values,
                        linewidth="0", marker=".")
        return line_obj

    def add_fit_line(self, spectrum_obj, line_objects):
        if spectrum_obj.fitting_parameters is not None:
            line_objects.append(self.get_line_obj_fit(spectrum_obj))
        return line_objects

    def get_line_obj_fit(self, spectrum_obj):
        x_values = spectrum_obj.frequency[spectrum_obj.plotting_indices]
        y_values = evaluate_lorentzian(x_values, spectrum_obj.fitting_parameters)
        line_obj = Line(x_values, y_values)
        return line_obj
