import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_file_contents_from_path

class SpectraValid(Feature):

    name = "Spectra Valid"
    peak_ratio_threshold = 11.5

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

    def load_necessary_data_for_saving(self):
        self.data_set_obj.spectra_raw("Load")

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
            if index >= 6:
                self.set_spectrum_peak_validity(spectrum_obj)
            else:
                spectrum_obj.has_valid_peak = False

    def set_spectrum_peak_validity(self, spectrum_obj):
        peak = np.max(spectrum_obj.S21)
        noise = np.median(spectrum_obj.S21)
        peak_ratio = peak / noise
        spectrum_obj.has_valid_peak = (peak_ratio > self.peak_ratio_threshold)

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
