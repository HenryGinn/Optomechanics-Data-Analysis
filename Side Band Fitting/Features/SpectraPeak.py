import os

import numpy as np

from Feature import Feature
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_file_contents_from_path

class SpectraPeak(Feature):

    name = "Spectra Peak"

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
        power_obj.spectra_peak_path = path
        make_folder(path)

    def set_trial_paths(self, power_obj):
        for trial_obj in power_obj.trial_objects:
            self.set_trial_path(trial_obj)
            self.set_detuning_paths(trial_obj)

    def set_trial_path(self, trial_obj):
        path = os.path.join(trial_obj.power_obj.spectra_peak_path, f"Trial {trial_obj.trial_number}")
        trial_obj.spectra_peak_path = path
        make_folder(path)

    def set_detuning_paths(self, trial_obj):
        for detuning_obj in trial_obj.detuning_objects:
            detuning_obj.spectra_peak_path = os.path.join(trial_obj.spectra_peak_path,
                                                     f"{detuning_obj.detuning} Hz.txt")

    def load_necessary_data_for_saving(self):
        self.data_set_obj.spectra_raw("Load")
        self.data_set_obj.spectra_valid("Load")

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
            if spectrum_obj.has_valid_peak:
                self.set_spectrum_peak(spectrum_obj)

    def set_spectrum_peak(self, spectrum_obj):
        peak_index = np.argmax(spectrum_obj.S21)
        spectrum_obj.peak_index = peak_index
        spectrum_obj.peak_S21 = spectrum_obj.S21[peak_index]
        spectrum_obj.peak_frequency = spectrum_obj.S21[peak_index]
        
    def save_detuning_obj(self, detuning_obj):
        with open(detuning_obj.spectra_peak_path, "w") as file:
            file.writelines("Spectrum index\tPeak index\tPeak S21\tPeak frequency (Hz)\n")
            self.save_detuning_obj_to_file(detuning_obj, file)

    def save_detuning_obj_to_file(self, detuning_obj, file):
        for index, spectrum_obj in enumerate(detuning_obj.spectrum_objects):
            if spectrum_obj.has_valid_peak:
                self.save_spectrum_obj_to_file(index, spectrum_obj, file)

    def save_spectrum_obj_to_file(self, index, spectrum_obj, file):
        peak_index = spectrum_obj.peak_index
        S21 = spectrum_obj.peak_S21
        frequency = spectrum_obj.peak_frequency
        file.writelines(f"{index}\t{peak_index}\t{S21}\t{frequency}\n")

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.spectra_peak_path)
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
        file_contents = get_file_contents_from_path(detuning_obj.spectra_peak_path)
        for index, peak_index, S21, frequency in zip(*file_contents):
            spectrum_obj = detuning_obj.spectrum_objects[int(index)]
            spectrum_obj.peak_index = int(peak_index)
            spectrum_obj.peak_S21 = S21
            spectrum_obj.peak_frequency = int(frequency)
