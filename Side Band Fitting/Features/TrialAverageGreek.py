import os
from copy import deepcopy

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Utils import make_folder
from Utils import get_file_contents_from_path
from Utils import get_moving_average
from Utils import mean_of_middle_values

class TrialAverageGreek(Feature):

    name = "Trial Average of Omega and Gamma"

    def __init__(self, data_set_obj):
        Feature.__init__(self, data_set_obj)
        self.set_commands()
    
    def set_paths(self):
        self.set_folder_path()
        for power_obj in self.data_set_obj.power_objects:
            file_name = f"{power_obj.power_string} dBm {self.name}.txt"
            path = os.path.join(self.folder_path, file_name)
            power_obj.trial_average_greek_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.average_greek("Load")

    def refresh_data(self):
        self.data_set_obj.average_greek("Refresh")

    def save_data_set_obj(self, data_set_obj):
        for power_obj in data_set_obj.power_objects:
            self.set_power_obj(power_obj)
            self.save_power_obj(power_obj)

    def set_power_obj(self, power_obj):
        self.set_detuning_dict(power_obj)
        self.set_gamma_data(power_obj)
        self.set_omega_data(power_obj)
        self.set_amplitude_data(power_obj)

    def set_detuning_dict(self, power_obj):
        detuning_objects = power_obj.trial_objects[0].detuning_objects
        power_obj.detunings = [detuning_obj.detuning for detuning_obj in detuning_objects]
        power_obj.detuning_dict = {detuning: [] for detuning in power_obj.detunings}

    def set_gamma_data(self, power_obj):
        gamma_values = self.get_gamma_values(power_obj)
        power_obj.gamma_mean = {detuning: np.mean(gamma_values[detuning])
                                for detuning in power_obj.detunings}
        power_obj.gamma_std = {detuning: np.std(gamma_values[detuning])
                                for detuning in power_obj.detunings}

    def get_gamma_values(self, power_obj):
        gamma_values = deepcopy(power_obj.detuning_dict)
        for trial_obj in power_obj.trial_objects:
            for detuning_obj in trial_obj.detuning_objects:
                if detuning_obj.gamma is not None:
                    gamma_values[detuning_obj.detuning].append(detuning_obj.gamma)
        return gamma_values

    def set_omega_data(self, power_obj):
        omega_values = self.get_omega_values(power_obj)
        power_obj.omega_mean = {detuning: np.mean(omega_values[detuning])
                                for detuning in power_obj.detunings}
        power_obj.omega_std = {detuning: np.std(omega_values[detuning])
                                for detuning in power_obj.detunings}

    def get_omega_values(self, power_obj):
        omega_values = deepcopy(power_obj.detuning_dict)
        for trial_obj in power_obj.trial_objects:
            for detuning_obj in trial_obj.detuning_objects:
                if detuning_obj.omega is not None:
                    omega_values[detuning_obj.detuning].append(detuning_obj.omega)
        return omega_values

    def set_amplitude_data(self, power_obj):
        amplitude_values = self.get_amplitude_values(power_obj)
        power_obj.amplitude_mean = {detuning: np.mean(np.log(amplitude_values[detuning]))
                                    for detuning in power_obj.detunings}
        power_obj.amplitude_std = {detuning: np.std(np.log(amplitude_values[detuning]))
                                   for detuning in power_obj.detunings}

    def get_amplitude_values(self, power_obj):
        amplitude_values = deepcopy(power_obj.detuning_dict)
        for trial_obj in power_obj.trial_objects:
            for detuning_obj in trial_obj.detuning_objects:
                if detuning_obj.amplitude is not None:
                    amplitude_values[detuning_obj.detuning].append(detuning_obj.amplitude)
        return amplitude_values

    def save_power_obj(self, power_obj):
        with open(power_obj.trial_average_greek_path, "w") as file:
            self.save_power_obj_to_file(power_obj, file)

    def save_power_obj_to_file(self, power_obj, file):
        self.write_file_header(file)
        for detuning_obj in power_obj.trial_objects[0].detuning_objects:
            self.save_greek_data_to_file(power_obj, detuning_obj.detuning, file)

    def write_file_header(self, file):
        file.writelines("Gamma Mean\tStandard Deviation of Gamma\t"
                        "Omega Mean\tStandard Deviation of Omega\t"
                        "Log(Amplitude Mean)\tStandard Deviation of Log(Amplitude)\n")

    def save_greek_data_to_file(self, power_obj, detuning, file):
        self.save_gamma_to_file(power_obj, detuning, file)
        self.save_omega_to_file(power_obj, detuning, file)
        self.save_amplitude_to_file(power_obj, detuning, file)

    def save_gamma_to_file(self, power_obj, detuning, file):
        gamma_mean = power_obj.gamma_mean[detuning]
        gamma_std = power_obj.gamma_std[detuning]
        file.writelines(f"{gamma_mean}\t{gamma_std}\t")

    def save_omega_to_file(self, power_obj, detuning, file):
        omega_mean = power_obj.omega_mean[detuning]
        omega_std = power_obj.omega_std[detuning]
        file.writelines(f"{omega_mean}\t{omega_std}\t")

    def save_amplitude_to_file(self, power_obj, detuning, file):
        amplitude_mean = power_obj.amplitude_mean[detuning]
        amplitude_std = power_obj.amplitude_std[detuning]
        file.writelines(f"{amplitude_mean}\t{amplitude_std}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(power_obj.trial_average_greek_path)
                       for power_obj in self.data_set_obj.power_objects])

    def do_load_data(self):
        for power_obj in self.data_set_obj.power_objects:
            path = power_obj.trial_average_greek_path
            greek_data = get_file_contents_from_path(path)
            self.load_from_greek_data(power_obj, greek_data)

    def load_from_greek_data(self, power_obj, greek_data):
        detunings = [detuning_obj.detuning for detuning_obj in power_obj.trial_objects[0].detuning_objects]
        power_obj.detunings = detunings
        power_obj.gamma_mean = {detuning: gamma_mean for detuning, gamma_mean in zip(detunings, greek_data[0])}
        power_obj.gamma_std = {detuning: gamma_std for detuning, gamma_std in zip(detunings, greek_data[1])}
        power_obj.omega_mean = {detuning: omega_mean for detuning, omega_mean in zip(detunings, greek_data[2])}
        power_obj.omega_std = {detuning: omega_std for detuning, omega_std in zip(detunings, greek_data[3])}
        power_obj.amplitude_mean = {detuning: amplitude_mean for detuning, amplitude_mean in zip(detunings, greek_data[4])}
        power_obj.amplitude_std = {detuning: amplitude_std for detuning, amplitude_std in zip(detunings, greek_data[5])}

    def create_plots(self):
        for power_obj in self.data_set_obj.power_objects:
            self.create_power_obj_plot(power_obj)

    def create_power_obj_plot(self, power_obj):
        lines_objects = self.get_lines_objects(power_obj)
        plots_obj = Plots(lines_objects)
        plots_obj.parent_results_path, _ = os.path.split(power_obj.trial_average_greek_path)
        plots_obj.title = f"{power_obj} Sideband Properties"
        plots_obj.plot()

    def get_lines_objects(self, power_obj):
        lines_objects = [self.get_gamma_lines_obj(power_obj),
                         self.get_omega_lines_obj(power_obj),
                         self.get_amplitude_lines_obj(power_obj)]
        return lines_objects

    def get_gamma_lines_obj(self, power_obj):
        x_values = power_obj.detunings
        y_values = list(power_obj.gamma_mean.values())
        y_err = list(power_obj.gamma_std.values())
        lines_obj = Lines([Line(x_values, y_values, y_err=y_err)], plot_type="errorbar")
        lines_obj.title = "Gamma"
        return lines_obj

    def get_omega_lines_obj(self, power_obj):
        x_values = power_obj.detunings
        y_values = list(power_obj.omega_mean.values())
        y_err = list(power_obj.omega_std.values())
        lines_obj = Lines([Line(x_values, y_values, y_err=y_err)], plot_type="errorbar")
        lines_obj.title = "Omega"
        return lines_obj

    def get_amplitude_lines_obj(self, power_obj):
        x_values = power_obj.detunings
        y_values = list(power_obj.amplitude_mean.values())
        y_err = list(power_obj.amplitude_std.values())
        lines_obj = Lines([Line(x_values, y_values, y_err=y_err)], plot_type="errorbar")
        lines_obj.title = "Log Amplitude"
        return lines_obj
