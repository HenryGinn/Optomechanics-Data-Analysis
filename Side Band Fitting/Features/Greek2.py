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

class Greek2(Feature):

    name = "Omega and Gamma 2"

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
        power_obj.greek_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)
            self.set_detuning_paths(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.greek_path, f"Trial {trial_obj.trial_number}")
        trial_obj.greek_path = path
        make_folder(path)

    def set_detuning_paths(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.trial_obj.greek_path, f"{detuning_obj.detuning} Hz.txt")
        detuning_obj.greek_path = path

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
            self.set_from_fit(spectrum_obj)
            
    def set_from_fit(self, spectrum_obj):
        if spectrum_obj.fitting_parameters is not None:
            self.do_set_from_fit(spectrum_obj)
        else:
            spectrum_obj.has_valid_peak = False
            spectrum_obj.gamma = None
            spectrum_obj.omega = None
            spectrum_obj.amplitude = None

    def do_set_from_fit(self, spectrum_obj):
        spectrum_obj.load_S21()
        spectrum_obj.set_fit_data()
        spectrum_obj.gamma = abs(spectrum_obj.fitting_parameters[1])
        spectrum_obj.set_amplitude_from_fit()
        spectrum_obj.set_omega_from_fit()
        spectrum_obj.omega = np.abs(spectrum_obj.omega)

    def save_detuning_obj(self, detuning_obj):
        with open(detuning_obj.greek_path, "w") as file:
            file.writelines("Spectrum Index\tGamma\tOmega\tAmplitude\n")
            self.save_detuning_obj_to_file(detuning_obj, file)

    def save_detuning_obj_to_file(self, detuning_obj, file):
        for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
            if spectrum_obj.has_valid_peak:
                self.save_spectrum_obj_to_file(spectrum_obj, index, file)

    def save_spectrum_obj_to_file(self, spectrum_obj, index, file):
        gamma = spectrum_obj.gamma
        omega = spectrum_obj.omega
        amplitude = spectrum_obj.amplitude
        file.writelines(f"{index}\t{gamma}\t{omega}\t{amplitude}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.greek_path)
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
        file_contents = get_file_contents_from_path(detuning_obj.greek_path)
        indices, gammas, omegas, amplitudes = file_contents
        for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
            if index in indices:
                spectrum_obj.has_valid_peak = True
                spectrum_obj.gamma = gammas[list(indices).index(index)]
                spectrum_obj.omega = omegas[list(indices).index(index)]
                spectrum_obj.amplitude = amplitudes[list(indices).index(index)]
            else:
                spectrum_obj.has_valid_peak = False
                spectrum_obj.gamma = None
                spectrum_obj.omega = None
                spectrum_obj.amplitude = None

    def create_plots(self):
        for power_obj in self.data_set_obj.power_objects:
            for trial_obj in power_obj.trial_objects:
                for detuning_obj in trial_obj.detuning_objects:
                    self.create_detuning_plot(detuning_obj)

    def create_detuning_plot(self, detuning_obj):
        lines_objects = self.get_lines_objects(detuning_obj)
        plots_obj = Plots(lines_objects)
        plots_obj.parent_results_path, _ = os.path.split(detuning_obj.greek_path)
        plots_obj.title = str(detuning_obj)
        plots_obj.plot()

    def get_lines_objects(self, detuning_obj):
        lines_objects = [self.get_gamma_lines_obj(detuning_obj),
                         self.get_omega_lines_obj(detuning_obj),
                         self.get_amplitude_lines_obj(detuning_obj)]
        return lines_objects

    def get_gamma_lines_obj(self, detuning_obj):
        line_obj = self.get_gamma_line_obj(detuning_obj)
        lines_obj = Lines([line_obj])
        lines_obj.title = "Gamma"
        return lines_obj

    def get_gamma_line_obj(self, detuning_obj):
        values = [(index, spectrum_obj.gamma)
                  for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects)
                  if spectrum_obj.has_valid_peak]
        x_values, y_values = zip(*values)
        line_obj = Line(x_values, y_values)
        return line_obj

    def get_omega_lines_obj(self, detuning_obj):
        line_obj = self.get_omega_line_obj(detuning_obj)
        lines_obj = Lines([line_obj])
        lines_obj.title = "Omega"
        return lines_obj

    def get_omega_line_obj(self, detuning_obj):
        values = [(index, spectrum_obj.omega)
                  for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects)
                  if spectrum_obj.has_valid_peak]
        x_values, y_values = zip(*values)
        line_obj = Line(x_values, y_values)
        return line_obj

    def get_amplitude_lines_obj(self, detuning_obj):
        line_obj = self.get_amplitude_line_obj(detuning_obj)
        lines_obj = Lines([line_obj])
        lines_obj.title = "Amplitude"
        return lines_obj

    def get_amplitude_line_obj(self, detuning_obj):
        values = [(index, spectrum_obj.amplitude)
                  for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects)
                  if spectrum_obj.has_valid_peak]
        x_values, y_values = zip(*values)
        line_obj = Line(x_values, y_values)
        return line_obj
