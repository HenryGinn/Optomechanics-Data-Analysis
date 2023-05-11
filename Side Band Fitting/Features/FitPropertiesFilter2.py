import os

import numpy as np
import scipy as sc

from Feature import Feature
from Spectrum import Spectrum
from Features.GetFittingParameters import get_fitting_parameters
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path
from Utils import evaluate_lorentzian

class FitPropertiesFilter2(Feature):

    name = "Fit Properties Filter 2"
    z_score_threshold = 2

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
        power_obj.fit_properties_filter2_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)
            self.set_detuning_paths(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.fit_properties_filter2_path, f"Trial {trial_obj.trial_number}")
        trial_obj.fit_properties_filter2_path = path
        make_folder(path)

    def set_detuning_paths(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_path(detuning_obj)

    def set_detuning_path(self, detuning_obj):
        path = os.path.join(detuning_obj.trial_obj.fit_properties_filter2_path, f"{detuning_obj.detuning} Hz.txt")
        detuning_obj.fit_properties_filter2_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.spectra_fit_filtered("Load")
        self.data_set_obj.greek("Load")

    def refresh_data(self):
        self.data_set_obj.spectra_fit_filtered("Refresh")
        self.data_set_obj.greek("Refresh")

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
        self.set_fit_heuristic_distribution(detuning_obj)
        for spectrum_obj in detuning_obj.spectrum_objects:
            self.set_spectrum_obj(spectrum_obj)

    def set_fit_heuristic_distribution(self, detuning_obj):
        self.set_spectrum_valid_first_pass(detuning_obj)
        gamma, omega, amplitude = self.get_fit_properties(detuning_obj)
        self.gamma_mean, self.gamma_std = self.get_distribution_parameters(gamma)
        self.omega_mean, self.omega_std = self.get_distribution_parameters(omega)
        self.amplitude_mean, self.amplitude_std = self.get_distribution_parameters(amplitude)
        print(detuning_obj, round(self.gamma_mean, 1), round(self.gamma_std, 2))

    def set_spectrum_valid_first_pass(self, detuning_obj):
        for spectrum_obj in detuning_obj.spectrum_objects:
            z_scores = np.array([spectrum_obj.gamma_z_score, self.spectrum_obj.omega_z_score, spectrum_obj.amplitude_z_score])
            spectrum_obj.first_pass = np.all((z_scores < self.z_score_threshold))

    def get_fit_properties(self, detuning_obj):
        fit_properties = [(spectrum_obj.gamma, spectrum_obj.omega, spectrum_obj.amplitude)
                          for spectrum_obj in detuning_obj.spectrum_objects
                          if spectrum_obj.first_pass]
        fit_properties_not_none = [properties for properties in fit_properties
                                   if None not in properties]
        return zip(*fit_properties_not_none)

    def get_distribution_parameters(self, data):
        mean = np.median(data)
        standard_deviation = sc.stats.median_abs_deviation(data)
        return mean, standard_deviation

    def set_spectrum_obj(self, spectrum_obj):
        self.set_gamma_filter(spectrum_obj)
        self.set_omega_filter(spectrum_obj)
        self.set_amplitude_filter(spectrum_obj)

    def set_gamma_filter(self, spectrum_obj):
        if spectrum_obj.first_pass:
            spectrum_obj.gamma_z_score2 = abs(spectrum_obj.gamma - self.gamma_mean) / self.gamma_std
        else:
            spectrum_obj.gamma_z_score2 = 1000

    def set_omega_filter(self, spectrum_obj):
        if spectrum_obj.first_pass:
            spectrum_obj.omega_z_score2 = abs(spectrum_obj.omega - self.omega_mean) / self.omega_std
            #spectrum_obj.valid_omega2  = (omega_z_score < self.z_score_threshold or omega_z_score < 0)
        else:
            spectrum_obj.omega_z_score2 = 1000

    def set_amplitude_filter(self, spectrum_obj):
        if spectrum_obj.first_pass:
            spectrum_obj.amplitude_z_score2 = abs(spectrum_obj.amplitude - self.amplitude_mean) / self.amplitude_std
            #spectrum_obj.valid_amplitude  = (amplitude_z_score < self.z_score_threshold or amplitude_z_score < 0)
        else:
            spectrum_obj.amplitude_z_score2 = 1000

    def save_detuning_obj(self, detuning_obj):
        with open(detuning_obj.fit_properties_filter2_path, "w") as file:
            file.writelines("Spectrum Index\tValid Gamma\tValid Omega\tValid Amplitude\n")
            self.save_detuning_obj_to_file(detuning_obj, file)

    def save_detuning_obj_to_file(self, detuning_obj, file):
        for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
            if spectrum_obj.has_valid_peak:
                self.save_spectrum_obj_to_file(spectrum_obj, index, file)

    def save_spectrum_obj_to_file(self, spectrum_obj, index, file):
        #valid_gamma = int(spectrum_obj.valid_gamma)
        #valid_omega = int(spectrum_obj.valid_omega)
        #valid_amplitude = int(spectrum_obj.valid_amplitude)
        valid_gamma = spectrum_obj.gamma_z_score
        valid_omega = spectrum_obj.omega_z_score
        valid_amplitude = spectrum_obj.amplitude_z_score
        file.writelines(f"{index}\t{valid_gamma}\t{valid_omega}\t{valid_amplitude}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.fit_properties_filter2_path)
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
        file_contents = get_file_contents_from_path(detuning_obj.fit_properties_filter2_path)
        if len(file_contents) > 0:
            indices, valid_gammas, valid_omegas, valid_amplitudes = file_contents
            for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
                if index in indices:
                    list_index = list(indices).index(index)
                    spectrum_obj.gamma_z_score2 = valid_gammas[list_index]
                    spectrum_obj.omega_z_score2 = valid_omegas[list_index]
                    spectrum_obj.amplitude_z_score2 = valid_amplitudes[list_index]
                else:
                    spectrum_obj.gamma_z_score2 = 1000
                    spectrum_obj.omega_z_score2 = 1000
                    spectrum_obj.amplitude_z_score2 = 1000
    
    def load_necessary_data_for_plotting(self):
        self.data_set_obj.spectra_fit("Load")

    def create_plots(self, **kwargs):
        self.set_colour_lookup()
        for power_obj in self.data_set_obj.power_objects:
            for trial_obj in power_obj.trial_objects:
                for detuning_obj in trial_obj.detuning_objects:
                    self.create_detuning_plot(detuning_obj, **kwargs)

    def set_colour_lookup(self):
        self.colour_lookup = {(False, False, False): "black",
                              (False, False, True): "black",
                              (False, True, False): "lime",
                              (False, True, True): "red",
                              (True, False, False): "lime",
                              (True, False, True): "yellow",
                              (True, True, False): "lime",
                              (True, True, True): "lime"}

    def create_detuning_plot(self, detuning_obj, **kwargs):
        lines_objects = self.get_lines_objects(detuning_obj)
        plots_obj = Plots(lines_objects, **kwargs)
        plots_obj.parent_results_path, _ = os.path.split(detuning_obj.fit_properties_filter2_path)
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
        peak_index = np.argmax(spectrum_obj.S21)
        left_index = peak_index - 150
        right_index = peak_index + 150
        spectrum_obj.plotting_indices = slice(left_index, right_index)
    
    def get_line_obj_S21(self, spectrum_obj):
        x_values = spectrum_obj.frequency[spectrum_obj.plotting_indices]
        y_values = spectrum_obj.S21[spectrum_obj.plotting_indices]
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
        colour = self.get_fit_line_colour(spectrum_obj)
        line_obj = Line(x_values, y_values, colour=colour)
        return line_obj

    def get_fit_line_colour(self, spectrum_obj):
        valid_property_key = (spectrum_obj.gamma_z_score2 < self.z_score_threshold,
                              spectrum_obj.omega_z_score2 < self.z_score_threshold,
                              True)
        return self.colour_lookup[valid_property_key]
