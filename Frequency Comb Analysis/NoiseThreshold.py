import os

import numpy as np

from CombFunction import CombFunction
from Spectrum import Spectrum
from Utils import make_folder
from Utils import get_file_contents_from_path

class NoiseThreshold(CombFunction):

    name = "Noise Threshold"
    window_width = 10
    noise_multiplier_threshold = 1.5

    def __init__(self, data_set_obj):
        CombFunction.__init__(self, data_set_obj)
        self.set_commands()

    def set_paths(self):
        self.set_folder_path()
        for drift_obj in self.data_set_obj.drift_objects:
            self.set_drift_path(drift_obj)
            self.set_detuning_paths(drift_obj)

    def set_drift_path(self, drift_obj):
        path = os.path.join(self.folder_path, drift_obj.folder_name)
        drift_obj.noise_threshold_path = path
        make_folder(path)

    def set_detuning_paths(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            path = os.path.join(drift_obj.noise_threshold_path,
                                f"{detuning_obj.detuning} Hz.txt")
            detuning_obj.noise_threshold_path = path


    def load_necessary_data_for_saving(self):
        self.data_set_obj.average_groups("Load")

    def save_data_set_obj(self, data_set_obj):
        for drift_obj in data_set_obj.drift_objects:
            self.save_drift_obj(drift_obj)

    def save_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.save_data_detuning(detuning_obj)

    def data_is_saved(self):
        return np.all([os.path.exists(detuning_obj.noise_threshold_path)
                       for drift_obj in self.data_set_obj.drift_objects
                       for detuning_obj in drift_obj.detuning_objects])

    def save_data_detuning(self, detuning_obj):
        self.set_noise_threshold(detuning_obj.spectrum_obj)
        self.save_noise_threshold(detuning_obj)

    def set_noise_threshold(self, spectrum_obj):
        spectrum_obj.noise_threshold = [self.get_noise_threshold(spectrum_obj, index)
                                        for index in range(len(spectrum_obj.S21))]

    def get_noise_threshold(self, spectrum_obj, index):
        S21_within_window = self.get_S21_within_window(spectrum_obj, index)
        noise_threshold = np.median(S21_within_window) * self.noise_multiplier_threshold
        return noise_threshold

    def get_S21_within_window(self, spectrum_obj, index):
        left_index = max(0, index - self.window_width)
        right_index = min(len(spectrum_obj.S21) - 1, index + self.window_width)
        S21_within_window = np.minimum(spectrum_obj.S21, 10**-11)[left_index:right_index]
        return S21_within_window

    def save_noise_threshold(self, detuning_obj):
        with open(detuning_obj.noise_threshold_path, "w") as file:
            file.writelines("Frequency (Hz)\tNoise Threshold (mW)\n")
            self.save_noise_threshold_to_file(detuning_obj.spectrum_obj, file)

    def save_noise_threshold_to_file(self, spectrum_obj, file):
        for frequency, noise in zip(spectrum_obj.frequency,
                                    spectrum_obj.noise_threshold):
            file.writelines(f"{frequency}\t{noise}\n")

    def do_load_data(self):
        for drift_obj in self.data_set_obj.drift_objects:
            self.load_drift_obj(drift_obj)

    def load_drift_obj(self, drift_obj):
        for detuning_obj in drift_obj.detuning_objects:
            self.load_detuning_obj(detuning_obj)
        
    def load_detuning_obj(self, detuning_obj):
        self.create_spectrum_object(detuning_obj)
        path = detuning_obj.noise_threshold_path
        _, detuning_obj.spectrum_obj.noise_threshold = get_file_contents_from_path(path)

    def create_spectrum_object(self, detuning_obj):
        if not hasattr(detuning_obj, "spectrum_obj"):
            detuning_obj.spectrum_obj = Spectrum(self)
