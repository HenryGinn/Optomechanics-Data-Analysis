import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Plotting.Plots import Plots
from Plotting.Lines import Lines
from Plotting.Line import Line
from Features.TransmissionFittingParameters import get_transmission_fitting_parameters
from Utils import make_folder
from Utils import get_file_contents_from_path
from Utils import evaluate_lorentzian

class TransmissionFit(Feature):

    name = "Transmission Fit"

    def __init__(self, data_set_obj):
        Feature.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        self.set_folder_path()
        for power_obj in self.data_set_obj.power_objects:
            self.set_power_path(power_obj)
            self.set_trial_paths(power_obj)

    def set_power_path(self, power_obj):
        path = os.path.join(self.folder_path, power_obj.folder_name)
        power_obj.transmission_fit_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.transmission_fit_path,
                            f"Trial {trial_obj.trial_number}.txt")
        trial_obj.transmission_fit_path = path

    def save_data_set_obj(self, data_set_obj):
        for power_obj in data_set_obj.power_objects:
            self.save_power_obj(power_obj)

    def save_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            print("")
            print(power_obj.power_string)
            self.set_trial_obj(trial_obj)
            self.save_trial_obj(trial_obj)

    def set_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_obj(detuning_obj)

    def set_detuning_obj(self, detuning_obj):
        transmission_obj = detuning_obj.transmission_obj
        transmission_obj.load_S21()
        transmission_obj.fitting_parameters = get_transmission_fitting_parameters(transmission_obj)
        omega_c = transmission_obj.fitting_parameters[3] # true peak of transmission
        omega_d = detuning_obj.cavity_frequency - detuning_obj.detuning
        detuning_obj.true_detuning = omega_c - omega_d
        detuning_obj.true_detuning = detuning_obj.detuning

    def save_trial_obj(self, trial_obj):
        with open(trial_obj.transmission_fit_path, "w") as file:
            file.writelines("Detuning (Hz)\tTrue Detuning (Hz)\tF\tGamma\tNoise\tResonant\n")
            self.save_trial_obj_to_file(trial_obj, file)

    def save_trial_obj_to_file(self, trial_obj, file):
        for detuning_obj in trial_obj.detuning_objects:
            detuning = detuning_obj.detuning
            true_detuning = detuning_obj.true_detuning
            F, gamma, noise, resonant = detuning_obj.transmission_obj.fitting_parameters
            file.writelines(f"{detuning}\t{true_detuning}\t{F}\t{gamma}\t{noise}\t{resonant}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(trial_obj.transmission_fit_path)
                       for power_obj in self.data_set_obj.power_objects
                       for trial_obj in power_obj.trial_objects])

    def do_load_data(self):
        for power_obj in self.data_set_obj.power_objects:
            self.load_power_obj(power_obj)

    def load_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.load_trial_obj(trial_obj)

    def load_trial_obj(self, trial_obj):
        file_contents = get_file_contents_from_path(trial_obj.transmission_fit_path)
        file_contents = list(zip(*file_contents))
        for detuning_obj, detuning_data in zip(trial_obj.detuning_objects, file_contents):
            detuning_obj.true_detuning = detuning_data[1]
            detuning_obj.transmission_obj.fitting_parameters = detuning_data[2:]

    def create_plots(self, **kwargs):
        for power_obj in self.data_set_obj.power_objects:
            for trial_obj in power_obj.trial_objects:
                self.create_plots_trial(trial_obj, **kwargs)

    def create_plots_trial(self, trial_obj, **kwargs):
        lines_objects = self.get_lines_objects(trial_obj)
        plots_obj = Plots(lines_objects, **kwargs)
        plots_obj.parent_results_path, _ = os.path.split(trial_obj.transmission_fit_path)
        plots_obj.title = f"{trial_obj} Transmission Fits"
        plots_obj.plot()

    def get_lines_objects(self, trial_obj):
        lines_objects = [self.get_lines_obj(detuning_obj)
                         for detuning_obj in trial_obj.detuning_objects]
        return lines_objects

    def get_lines_obj(self, detuning_obj):
        transmission_obj = detuning_obj.transmission_obj
        transmission_obj.load_S21()
        line_objects = [self.get_line_obj_transmission(transmission_obj)]
        self.add_line_obj_fit(transmission_obj, line_objects)
        lines_obj = Lines(line_objects)
        lines_obj.title = f"{detuning_obj.detuning} Hz"
        return lines_obj

    def get_line_obj_transmission(self, transmission_obj):
        x_values = transmission_obj.frequency
        y_values = transmission_obj.S21
        line_obj = Line(x_values, y_values)
        return line_obj

    def add_line_obj_fit(self, transmission_obj, line_objects):
        if transmission_obj.fitting_parameters is not None:
            x_values = transmission_obj.frequency
            y_values = evaluate_lorentzian(x_values, transmission_obj.fitting_parameters)
            line_obj = Line(x_values, y_values, colour="grey", linestyle="--")
            line_objects.append(line_obj)
