import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from DataFit import DataFit
from Utils import make_folder
from Utils import get_file_contents_from_path

class Greek(Feature):

    name = "Omega and Gamma"

    def __init__(self, data_set_obj):
        Feature.__init__(self, data_set_obj)
        self.set_commands()

    def process_kwargs(self, **kwargs):
        self.kwargs = kwargs
        self.process_average_size()

    def process_average_size(self):
        if "average" in self.kwargs:
            self.average_size = self.kwargs["average"]
        else:
            self.average_size = None

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

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.greek_path, f"Trial {trial_obj.trial_number}.txt")
        trial_obj.greek_path = path

    def load_necessary_data_for_saving(self):
        self.data_set_obj.average_spectra("Load", average=self.average_size)

    def save_data_set_obj(self, data_set_obj):
        for power_obj in data_set_obj.power_objects:
            self.save_power_obj(power_obj)

    def save_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_obj(trial_obj)
            self.save_trial_obj(trial_obj)

    def set_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_obj(detuning_obj)

    def set_detuning_obj(self, detuning_obj):
        for spectrum_obj in detuning_obj.average_spectrum_objects:
            self.set_spectrum_obj(spectrum_obj)

    def set_spectrum_obj(self, spectrum_obj):
        data_fit_obj = DataFit(spectrum_obj)
        spectrum_obj.fit_function = data_fit_obj.evaluate_lorentzian
        spectrum_obj.initial_fitting_parameters = data_fit_obj.get_initial_fitting_parameters()
        spectrum_obj.fitting_parameters = data_fit_obj.get_automatic_fit(spectrum_obj.initial_fitting_parameters)
        spectrum_obj.gamma = data_fit_obj.get_gamma_from_fit()
        spectrum_obj.set_amplitude_from_fit()
        spectrum_obj.set_omega_from_fit()

    def save_trial_obj(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            self.set_detuning_obj(detuning_obj)
            self.save_detuning_obj(detuning_obj)

    def save_detuning_obj(self, detuning_obj):
        pass

    def data_is_saved(self):
        return np.all([os.path.exists(trial_obj.greek_path)
                       for power_obj in self.data_set_obj.power_objects
                       for trial_obj in power_obj.trial_objects])

    def do_load_data(self):
        for power_obj in self.data_set_obj.power_objects:
            self.load_power_obj(power_obj)

    def load_power_obj(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.load_trial_obj(trial_obj)

    def load_trial_obj(self, trial_obj):
        pass
